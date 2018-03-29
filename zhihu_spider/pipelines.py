# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pykafka import KafkaClient
from redis import Redis
import pymysql
import time

'''
    从任务队列获取问题，爬取问题的实时数据
    1、若有历史数据，则取出mysql历史数据，与最新数据送入kafka
    2、若无历史数据，不送入kafka
    3、则将最新数据存入mysql
'''
class QuestionPipeline(object):


    def open_spider(self, spider):
        self.key = '%s:%s' % ('zhihu', 'question')
        self.redis_client = Redis(host='localhost', port=6379, db=0, password=None)
        self.mysql_client = pymysql.connect(host="localhost", user="root", password="root", db="zhihu", charset="utf8")

        client = KafkaClient(hosts="slave02:9092, slave01:9092, master:9092")
        topic = client.topics[b'question']  # 选择一个topic
        self.kafka_producer = topic.get_producer()


    def close_spider(self, spider):
        self.redis_client = None
        self.mysql_client.close()
        self.kafka_producer.stop()


    def process_item(self, item, spider):
        # {'json': {'answer_count': '6',
        #           'coment_count': 0,
        #           'follower_count': '66',
        #           'id': '268705003',
        #           'question': '每一世代的主机都是如何遭到破解的？破解给他们造成了什么样的影响？',
        #           'topics': [{'游戏': '//www.zhihu.com/topic/19550994'},
        #                      {'任天堂 (Nintendo)': '//www.zhihu.com/topic/19552393'},
        #                      {'游戏机': '//www.zhihu.com/topic/19554542'},
        #                      {'索尼 (Sony)': '//www.zhihu.com/topic/19566440'},
        #                      {'家用游戏机': '//www.zhihu.com/topic/19611203'}],
        #           'view_count': '25440'}}
        print(item)

        id = item['json']['id']
        answer_count = item['json']['answer_count'].replace(',','')
        coment_count = item['json']['coment_count']
        follower_count = item['json']['follower_count']
        view_count = item['json']['view_count']
        insert_time = time.strftime("%Y-%m-%d %H:%M:%S")

        title = item['json']['question']
        topics = {}
        for i in item['json']['topics']:
            topic = i.popitem()
            topic_name = topic[0]
            topic_id = topic[1].split("/")[-1]
            topics[topic_id]=topic_name


        # 送入kafka, 根据 id 查询 question_measure 是否有历史数据
        cursor = self.mysql_client.cursor()
        cursor.execute(
            'SELECT create_time FROM question WHERE id='+ str(id) )
        create_time = ""
        for c in cursor:
            create_time = c[0]


        re = cursor.execute(
            'SELECT answer_count,coment_count,follower_count,view_count,insert_time FROM question_measure WHERE id='
            +id+' ORDER BY insert_time DESC LIMIT 1')

        if re > 0:
            data={}
            for i in cursor:
                # 送入kafka
                data = {
                    "id"            : id,
                    "create_time"   : create_time,
                    "answer"        : answer_count,
                    "follower"      : follower_count,
                    "view"          : view_count,
                    "insert_time"    : insert_time,

                    "last_answer"       : i[0],
                    "last_follower"     : i[2],
                    "last_view"         : i[3],
                    "last_insert_time"   : i[4],

                }

            self.kafka_producer.produce(bytes(str(data),encoding="utf-8"))


        # 将数据存入持久化到 mysql中
        cursor.execute(
            'INSERT INTO question_measure(id, answer_count, coment_count, follower_count, view_count, insert_time)'
            'VALUES ("%s", "%s", "%s", "%s", "%s", "%s") '
            % (id, answer_count, coment_count, follower_count, view_count, insert_time))
        cursor.execute('UPDATE question set update_time="%s", topics="%s", title="%s"'
                       'WHERE id="%s"' % (insert_time, topics, title, id))
        self.mysql_client.commit()
        cursor.close()





'''
    每隔一段时间，爬取根话题的Top50问答
    1、id放入redis任务集合，去重√
    2、question数据持久化到mysql中
'''
class RootPipeline(object):


    def open_spider(self, spider):
        self.key = '%s:%s' % ('zhihu', 'question')
        self.redis_client = Redis(host='localhost', port=6379, db=0, password=None)
        self.mysql_client = pymysql.connect(host="localhost", user="root", password="root", db="zhihu", charset="utf8")


    def close_spider(self, spider):
        self.redis_client = None
        self.mysql_client.close()


    def process_item(self, item, spider):
        items = item['json']['data']
        for i in items:
            if i['target']['type'] == 'answer':
                # 获取问题标题、创建时间   https://www.zhihu.com/api/v4/questions/46447275
                question = i['target']['question']
                id = question['id']
                title = question['title']
                type = question['type']
                question_type = question['question_type']
                create_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(question['created'])))
                insert_time = time.strftime("%Y-%m-%d %H:%M:%S")


                # 放入redis队列
                x = self.redis_client.sadd(self.key,id)
                print("放入redis队列,id=" + str(id) + " re:" + str(x))


                # 持久化到mysql中
                cursor = self.mysql_client.cursor()
                cursor.execute('INSERT INTO question(id, title, type, question_type, create_time, insert_time)'
                                'VALUES ''("%s", "%s", "%s", "%s", "%s", "%s") '
                                'ON DUPLICATE KEY UPDATE type="%s"'
                                % (id, title, type, question_type, create_time, insert_time, type))

                self.mysql_client.commit()
                cursor.close()
        return None




if __name__=='__main__':
    begin = time.time()

    # client = KafkaClient(hosts="slave02:9092, slave01:9092, master:9092")  # 可接受多个Client这是重点
    # topic = client.topics  # 查看所有topic
    # topic = client.topics[b'test1']  # 选择一个topic
    # producer = topic.get_producer()
    # fp = open('D:/logs/bdp.log')
    # i = 0
    # for line in range(1000):
    #     producer.produce(b"aaaaaaaaaa")
    #
    # producer.produce(b"continue")
    # time.sleep(10)
    # for line in range(1000):
    #     producer.produce(b"bbbbbbbbbbb")
    #
    # producer.produce(b"over")
    # end = time.time()
    # print("use time:" + str((end - begin)))
    # time.sleep(100)
    # producer.stop()
    # print("over")


    # print(str(client.sadd("key", "123")))
    # print(str(client.sadd("key", "1234")))
    # print(str(client.smembers("key")))
    # print(str(type(client.spop("key"))))
    # print(str(client.spop("key")))
    # print(str(client.spop("key")))
    # print(str(client.spop("key")))
    # print(str(client.spop("key")))
    # print(str(client.spop("key")==None))


    # # 转换成localtime
    # time_local = time.localtime(1521088267)
    # # 转换成新的时间格式(2016-05-05 20:28:54)
    # dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    # print(dt)
    # time_local = time.localtime()
    # # 转换成新的时间格式(2016-05-05 20:28:54)
    # dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    # print(dt)
    # print(time.time())
    # print(time.localtime())
    # print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int("1521088267"))))

    mysql_client = pymysql.connect(host="localhost", user="root", password="root", db="zhihu", charset="utf8")
    cursor =  mysql_client.cursor()
    re = cursor.execute('SELECT id FROM question WHERE create_time > "2016-01-01"')

    client = Redis(host='localhost', port=6379, db=0, password=None)
    for i in cursor:
        print(str(client.sadd("zhihu:question", i[0])))





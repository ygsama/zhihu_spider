# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.http import Request
from redis import Redis
import json
from zhihu_spider.items import QuestionSpiderItem
from bs4 import BeautifulSoup
from zhihu_spider.config import (
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, DEFAULT_REDIS_DB,
)

class Questionpider(scrapy.Spider):
    name = "question"
    allowed_domains = ["zhihu.com"]
    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Origin": "https://www.zhihu.com",
        "Referer": "https://www.zhihu.com/topic/19776749/hot",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    # HTTPERROR_ALLOWED_CODES=[404]
    handle_httpstatus_list = [404]

    custom_settings = {

        "DOWNLOAD_DELAY": 2.5,  # 延迟时间，秒
        # "CLOSESPIDER_PAGECOUNT": 50,  # 爬取请求次数限制
        'ITEM_PIPELINES': {
            'zhihu_spider.pipelines.QuestionPipeline': 100,
        }

    }

    start_urls = []
    url = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.key = '%s:%s' % ('zhihu', 'question')
        self.redis_client = Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=DEFAULT_REDIS_DB, password=REDIS_PASSWORD)


    def start_requests(self):
        self.id = self.redis_client.spop(self.key)

        while True:
            if id == None:
                time.sleep(10)
                self.id = self.redis_client.spop(self.key)
            else:
                url = "https://www.zhihu.com/question/" + bytes.decode(self.id)
                break

        yield Request(url, headers=self.header, method="GET", dont_filter=True , encoding='utf-8',callback=self.parse)

    def parse(self, response):
        if response.status != 404:
            data = {}
            soup = BeautifulSoup(response.body_as_unicode(), "lxml")
            # print(soup.prettify())


            items = soup.select('strong[class="NumberBoard-itemValue"]')
            data['id'] = bytes.decode(self.id)
            data['follower_count'] = items[0]['title']   # 问题关注人数
            data['view_count'] = items[1]['title']       # 问题浏览次数
            data['question'] = str(soup.select('.QuestionHeader-title')[0]).split("-->")[1].split("<!--")[0] # 问题
            data['answer_count'] = str(soup.select('.List-headerText')[0].span).split("-->")[1].split("<!--")[0] # 回答数


            data['topics'] = []
            topics = soup.select('.TopicLink')
            for t in topics:
                topic_href = t["href"]      # 话题url
                topic = t.div.div.string    # 话题
                data['topics'].append({topic:topic_href})


            data['coment_count'] = 0  # 评论数
            if  str(soup.select('.QuestionHeader-Comment')[0]).split("评论")[0].split("-->")[-1] != "添加":
                data['coment_count'] = str(soup.select('.QuestionHeader-Comment')[0]).split("评论")[0].split("-->")[-1].split(" ")[0]


            item = QuestionSpiderItem()
            item['json'] = data
            yield item
        else:
            pass
            # TODO 移除reids集合，修改mysql问题状态


        self.id = self.redis_client.spop(self.key)
        while True:
            if self.id == None:
                time.sleep(10)
                self.id = self.redis_client.spop(self.key)
            else:
                url = "https://www.zhihu.com/question/" + bytes.decode(self.id)
                break
        yield Request(url, headers=self.header, method="GET", dont_filter=True, encoding='utf-8', callback=self.parse)


# if __name__=='__main__':


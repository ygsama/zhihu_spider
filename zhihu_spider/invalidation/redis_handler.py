#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import redis


'''
    
    list
        rpush   在列表的末尾插入一个元素
        blpop   从列表开头获取一个元素，如果列表是空则阻塞
        lpop    从列表开头获取一个元素，如果列表是空则返回空
        llen    返回列表的长度
        
    set
        sadd(name,values)               给name对应的集合中添加元素, r.sadd("set_name","aa","bb")
        srem(name, values)              删除name对应的集合中的某些值
        spop(name)                      随机删除一个元素，并将其返回
        smove(src, dst, value)          将某个元素从一个集合中移动到另外一个集合
        scard(name)                     获取name对应的集合中的元素个数
        smembers(name)                  获取name对应的集合的所有成员
        sdiff(keys, *args)              在第一个name对应的集合中且不在其他name对应的集合的元素集合
        sdiffstore(dest, keys, *args)   把sdiff获取的值加入到dest对应的集合中
        sinter(keys, *args)             获取多个name对应集合的并集
        sinterstore(dest, keys, *args)  获取多个name对应集合的并集，再将其加入到dest对应的集合中
        sismember(name, value)          检查value是否是name对应的集合内的元素
        srandmember(name, numbers)      从name对应的集合中随机获取numbers个元素
        sunion(keys, *args)             获取多个name对应的集合的并集
        sunionstore(dest,keys, *args)   获取多个name对应的集合的并集，并将结果保存到dest对应的集合中

'''
class RedisPool(object):


    def __init__(self, name, namespace='queue', **redis_kwargs):
        # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
        self.client = redis.Redis(**redis_kwargs)
        self.key = '%s:%s' % (namespace, name)

    def size(self):
        return self.client.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        self.client.rpush(self.key, item)  # 添加新元素到队列最右方

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.client.blpop(self.key, timeout=timeout)
        return bytes.decode(item[1])

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.client.lpop(self.key)
        return bytes.decode(item)

    def put_task_queue(self, task_queue_params):
        for item in task_queue_params:
            self.put(item)

#######################################################################

    def sadd(self,name,*values):
        self.client.sadd(name=name,*values)

    def spop(self,name):
        self.client.spop(name=name)



if __name__=='__main__':
    t = RedisPool('tasks_pool')
    t.put("aaa")
    # u = t.get_wait()
    # u1 = t.get_nowait()
    # print(u)
    print(t.get_wait())
    print(t.get_nowait())

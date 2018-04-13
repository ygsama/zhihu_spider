#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
__doc__ = '''Cookie池，将Cookie保存成json格式'''

from multiprocessing import Queue

class CookiesPool(object):

    def __init__(self, name, namespace='queue', **redis_kwargs):

        # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
        self.pool = redis.Redis(**redis_kwargs)
        self.key = '%s:%s' % (namespace, name)


    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.pool.blpop(self.key, timeout=timeout)
        if item:
            item = item[1]  # 返回值为一个tuple
        return eval(bytes.decode(item))

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.pool.lpop(self.key)
        return eval(bytes.decode(item))


    def put(self,cookie_dict):
        self.pool.rpush(self.key, cookie_dict)


    def init_cookie(self):
        with open('zhihu.cookie', 'r') as file:
            for line in file.readlines():
                if line == "":
                    continue
                cookie_dict = {}
                for cookie in line.split(';'):
                    k, v = cookie.strip().split('=', 1)  # 1代表只分割一次
                    cookie_dict[k] = v
                self.put(cookie_dict)

    def size(self):
        return self.pool.llen(self.key)  # 返回队列里面list内元素的数量


if __name__ == '__main__':
    pool = CookiesPool('cookies_pool')
    pool.init_cookie()
    c = pool.get_nowait()
    c1 = pool.get_wait()
    c2 = pool.get_wait()
    c3 = pool.get_wait()
    cookies = []
    cookies.append(c)
    cookies.append(c1)
    cookies.append(c2)
    cookies.append(c3)
    print(cookies)


"""
This module provides clients for apps.
"""


from zhihu_spider.client.py_cli import ProxyFetcher

from bs4 import BeautifulSoup
import requests

url = 'https://www.zhihu.com/'

proxies = {

    'http': "http://182.34.55.252:36260",

}

session = requests.Session()

r = session.get(url=url, proxies=proxies)
# r = requests.session().get(url, proxies=proxies)
soup = BeautifulSoup(r.text, 'lxml')
print(r.status_code)
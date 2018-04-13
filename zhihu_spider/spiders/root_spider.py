# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json

from zhihu_spider.items import RootSpiderItem


class RootSpider(scrapy.Spider):
    name = "root"
    allowed_domains = ["zhihu.com"]

    # 覆盖掉settings.py里的相同设置
    custom_settings = {
        # "CONCURRENT_REQUESTS" : 10,
        # "AUTOTHROTTLE_ENABLED ": True,      # 开启延迟爬取
        "DOWNLOAD_DELAY": 2.5,                  # 延迟时间，秒
        "CLOSESPIDER_PAGECOUNT": 4,          # 爬取请求次数限制


        'ITEM_PIPELINES': {
            'zhihu_spider.pipelines.RootPipeline': 100,
        }

    }

    header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.zhihu.com",
        "Origin": "https://www.zhihu.com",
        "Referer": "https://www.zhihu.com/topic/19776749/hot",
        "Upgrade-Insecure-Requests": "1",
        "X-Requested-With": "XMLHttpRequest"
    }

    start_urls = [
        "https://www.zhihu.com/api/v4/topics/19776749/feeds/top_activity?include=data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dquestion%29%5D.target.comment_count&limit=10&after_id="
    ]



    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=self.header, method="GET", dont_filter=True , callback=self.parse)


    def parse(self, response):

        item = RootSpiderItem()
        # 获取问题的数据，并保存到redis中
        item['json'] = json.loads(response.body_as_unicode())
        yield item

        # 获取根话题下一页的url，并发送请求
        url = item['json']['paging']['next']
        yield Request(url, headers=self.header, method="GET", dont_filter=True,callback=self.parse)
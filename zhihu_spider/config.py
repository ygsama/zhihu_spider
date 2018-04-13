AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2526.106 BIDUBrowser/8.7 Safari/537.36",
        ]

ZHIHU_COOKIE=r'E:\py_workspace\zhihu_spider\zhihu_spider\zhihu.cookie'

REDIS_HOST = '140.143.206.106'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
DEFAULT_REDIS_DB = 0


MYSQL_HOST = '140.143.206.106'
MYSQL_PORT = 3306
MYSQL_DB   = 'zhihu'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''


KAFKA_HOSTS = 'slave02:9092, slave01:9092, master:9092'
KAFKA_TOPICS = b'question'



#####################################################################
# Custom settings of this project
#####################################################################

# scheduler settings
TIMER_RECORDER = 'haipproxy:schduler:task'
LOCKER_PREFIX = 'haipproxy:lock:'

# proxies crawler's settings
SPIDER_FEED_SIZE = 10
SPIDER_COMMON_TASK = 'haipproxy:spider:common'
SPIDER_AJAX_TASK = 'haipproxy:spider:ajax'
SPIDER_GFW_TASK = 'haipproxy:spider:gfw'
SPIDER_AJAX_GFW_TASK = 'haipproxy:spider:ajax_gfw'

# data_all is a set , it's a dupefilter
DATA_ALL = 'haipproxy:all'
# the data flow is init queue->validated_queue->validator_queue(temp)->validated_queue(score queue)->
# ttl_queue, speed_qeuue -> clients
# http_queue is a list, it's used to store initially http/https proxy resourecs
INIT_HTTP_QUEUE = 'haipproxy:init:http'
# socks proxy resources container
INIT_SOCKS4_QUEUE = 'haipproxy:init:socks4'
INIT_SOCKS5_QUEUE = 'haipproxy:init:socks5'

# custom validator settings
VALIDATOR_FEED_SIZE = 50

# they are temp sets, come from init queue, in order to filter transparnt ip
TEMP_HTTP_QUEUE = 'haipproxy:http:temp'
TEMP_HTTPS_QUEUE = 'haipproxy:https:temp'
TEMP_WEIBO_QUEUE = 'haipproxy:weibo:temp'
TEMP_ZHIHU_QUEUE = 'haipproxy:zhihu:temp'

# valited queues are zsets.squid and other clients fetch ip resources from them.
VALIDATED_HTTP_QUEUE = 'haipproxy:validated:http'
VALIDATED_HTTPS_QUEUE = 'haipproxy:validated:https'
VALIDATED_WEIBO_QUEUE = 'haipproxy:validated:weibo'
VALIDATED_ZHIHU_QUEUE = 'haipproxy:validated:zhihu'

# time to life of proxy ip resources
TTL_VALIDATED_RESOURCE = 2  # minutes
TTL_HTTP_QUEUE = 'haipproxy:ttl:http'
TTL_HTTPS_QUEUE = 'haipproxy:ttl:https'
TTL_WEIBO_QUEUE = 'haipproxy:ttl:weibo'
TTL_ZHIHU_QUEUE = 'haipproxy:ttl:zhihu'

# queue for proxy speed
SPEED_HTTP_QUEUE = 'haipproxy:speed:http'
SPEED_HTTPS_QUEUE = 'haipproxy:speed:https'
SPEED_WEIBO_QUEUE = 'haipproxy:speed:weibo'
SPEED_ZHIHU_QUEUE = 'haipproxy:speed:zhihu'

# squid settings on linux os
# execute sudo chown -R $USER /etc/squid/ and
# sudo chown -R $USER /var/log/squid/cache.log at first
SQUID_BIN_PATH = '/usr/sbin/squid'  # mac os '/usr/local/sbin/squid'
SQUID_CONF_PATH = '/etc/squid/squid.conf'  # mac os '/usr/local/etc/squid.conf'
SQUID_TEMPLATE_PATH = '/etc/squid/squid.conf.backup'  # mac os /usr/local/etc/squid.conf.backup

# client settings
# client picks proxies which's response time is between 0 and 5 seconds
LONGEST_RESPONSE_TIME = 10
# client picks proxies which's score is not less than 7
LOWEST_SCORE = 7


##############################################################
# validator scheduler will fetch tasks from task queue and store into resource
# 校验器将从task_queue中获取代理IP，校验后存入resource，具体流程见 架构篇
VALIDATOR_TASKS = [
    {
        # 任务名，不能和其他任务同名
        'name': 'http',
        # 代理来源
        'task_queue': TEMP_HTTP_QUEUE,
        # 代理存入的地方
        'resource': VALIDATED_HTTP_QUEUE,
        # 定时校验间隔
        'internal': 20,  # 20 minutes
        # 是否启用
        'enable': 1,
    },
    {
        'name': 'https',
        'task_queue': TEMP_HTTPS_QUEUE,
        'resource': VALIDATED_HTTPS_QUEUE,
        'internal': 20,
        'enable': 1,
    },
    {
        'name': 'weibo',
        'task_queue': TEMP_WEIBO_QUEUE,
        'resource': VALIDATED_WEIBO_QUEUE,
        'internal': 20,
        'enable': 1,
    },
    {
        'name': 'zhihu',
        'task_queue': TEMP_ZHIHU_QUEUE,
        'resource': VALIDATED_ZHIHU_QUEUE,
        'internal': 20,
        'enable': 1,
    },
]

# crawlers will fetch tasks from the following queues
# 代理IP抓取爬虫对应映射
CRAWLER_TASK_MAPS = {
    'common': SPIDER_COMMON_TASK,
    'ajax': SPIDER_AJAX_TASK,
    'gfw': SPIDER_GFW_TASK,
    'ajax_gfw': SPIDER_AJAX_GFW_TASK
}

# validators will fetch proxies from the following queues
# 校验器将从下面队列中获取代理IP进行校验
TEMP_TASK_MAPS = {
    'init': INIT_HTTP_QUEUE,
    'http': TEMP_HTTP_QUEUE,
    'https': TEMP_HTTPS_QUEUE,
    'weibo': TEMP_WEIBO_QUEUE,
    'zhihu': TEMP_ZHIHU_QUEUE
}


# 以下三个maps的作用是存储和提供可用代理，代表三个维度
# todo the three maps may be combined in one map
# validator scheduler and clients will fetch proxies from the following queues
SCORE_MAPS = {
    'http': VALIDATED_HTTP_QUEUE,
    'https': VALIDATED_HTTPS_QUEUE,
    'weibo': VALIDATED_WEIBO_QUEUE,
    'zhihu': VALIDATED_ZHIHU_QUEUE
}

# validator scheduler and clients will fetch proxies from the following queues which are verified recently
TTL_MAPS = {
    'http': TTL_HTTP_QUEUE,
    'https': TTL_HTTPS_QUEUE,
    'weibo': TTL_WEIBO_QUEUE,
    'zhihu': TTL_ZHIHU_QUEUE
}

SPEED_MAPS = {
    'http': SPEED_HTTP_QUEUE,
    'https': SPEED_HTTPS_QUEUE,
    'weibo': SPEED_WEIBO_QUEUE,
    'zhihu': SPEED_ZHIHU_QUEUE
}
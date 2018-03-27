## 开发文档
####爬虫模块

- root爬虫

  爬取根话题的问答，将问题id放入`Redis任务队列`

  ​

- question爬虫

  从`Redis任务队列`取出任务，爬取问题信息，放入kafka队列

  ​

- cookie池

  存储账号cookie

  ​

- IP代理模块

  获取高匿IP



####Kafka集群







####web模块




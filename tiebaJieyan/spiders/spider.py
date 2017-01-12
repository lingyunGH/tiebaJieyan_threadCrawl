#-*-coding=utf-8-*-
import scrapy
import requests
from scrapy.selector import Selector
from tiebaJieyan.items import threadsItem
from json import loads
from scrapy.http import Request
from re import findall,split
import time
from mysql_model import Mysql
from tiebaJieyan.common.logger import Logger
mysql = Mysql()
#获取当前时间
cur_tm = time.localtime(time.time())
#获取当前年
cur_year = cur_tm.tm_year
#获取月
cur_month = cur_tm.tm_mon
#获取日
cur_day = cur_tm.tm_mday
loger = Logger('threads','threads.log')
class threadsSpider(scrapy.Spider):
    name = "threadsJieyan"
    baseurl = 'http://tieba.baidu.com/f?kw=%E6%88%92%E7%83%9F&ie=utf-8'
    start_urls = []
    #在命令行使用-a添加参数，ps(开始页)，pe（结束页）
    #不传参数默认爬取1-100页
    def __init__(self,ps=1,pe=100,*args, **kwargs):
        super(threadsSpider, self).__init__(*args, **kwargs)
        page_start = int(ps)
        page_end = int(pe)
        # print page_start
        # print page_end
        for i in range(page_start,page_end+1):
            self.start_urls.append(self.baseurl+'&pn=%d'%((i-1)*50))
        # ...

    def parse(self, response):
        selector = Selector(response)
        #获取当前页码
        if selector.xpath('//span[@class="pagination-current pagination-item "]/text()').extract():
                cur_pn = selector.xpath('//span[@class="pagination-current pagination-item "]/text()').extract()[0]
        else:  
                cur_pn = selector.xpath('//span[@class="pagination-current pagination-item eye-protector-processed"]/text()').extract()[0]
        # 获取普通帖
        # print response.body
        normalTie = selector.xpath('//li[@class=" j_thread_list clearfix"]')
        i=0
        for top in normalTie:
            threadItem = threadsItem()
            #避免出现空的
            #进字符串解析为json
            if top.xpath('./@data-field').extract():
                data_field = loads(top.xpath('./@data-field').extract()[0])
                # print dict(data_field)
                
                #帖子id
                thread_id = data_field['id']
                
                thread_id_sql = "select * from threads where thread_id='%s'"%thread_id
                res = mysql.find_data(thread_id_sql)
                if len(res)>0:
                    continue
                #回帖数


                rep_num = data_field['reply_num']
                threadItem['rep_num'] = rep_num
                # self.log(rep_num)
                # print u'回帖数目是：%s'%rep_num

                # print thread_id
                threadItem['thread_id'] = thread_id
                threadItem['thread_link'] = 'http://tieba.baidu.com/p/'+ str(thread_id)
                self.log(thread_id)
                # print thread_id

                #是否精品
                is_good = data_field['is_good']
                if  is_good:
                    threadItem['is_good'] = 1
                else:
                    threadItem['is_good'] = 0

                # print u'精帖？%d'%threadItem['is_good']
                # 发帖人姓名,部分帖子没有作者
                author_name = data_field['author_name']
                #删除主贴会不存在发帖人信息
                if author_name:
                    threadItem['author_name'] = author_name
                else:
                    threadItem['author_name'] = 'null'
                # print u'帖子作者是:%s' % author_name
                # self.log(author_name)

            # 帖子标题
            # if top.xpath('.//div[@class="threadlist_lz clearfix"]/div[1]/a/text()').extract():
            title = top.xpath('.//div[@class="threadlist_lz clearfix"]/div[1]/a/text()').extract()
            if title:
                res = title[0].split("'")
                if len(res)>0:
                    threadItem['title'] = ''.join(res)
                else:
                    threadItem['title'] = title[0] 

                # print u'帖子标题是:%s' % title
            
        
            #发帖人id
            user_id =  top.xpath('.//div[@class="threadlist_lz clearfix"]/div[@class="threadlist_author pull_right"]/span[1]/@data-field').extract()
            if user_id:
                threadItem['author_id'] = loads(user_id[0])['user_id']


            # 帖子创建时间
            create_time = top.xpath('.//span[@class="pull-right is_show_create_time"]/text()').extract()
            if create_time:
                create_time = create_time[0]
                #小时开始
                if findall(':',create_time):
                    threadItem['c_time'] = str(cur_year)+'-'+str(cur_month)+ '-' + str(cur_day)+' ' +create_time
                #从月开始
                elif len(split('-',create_time)[0])<=2:
                    threadItem['c_time'] = str(cur_year) + '-' + create_time
                #从年开始
                else:
                    threadItem['c_time'] = create_time

            # print threadItem['c_time']


            # # 用户主页
            # linkUser = top.xpath('//div[@class="t_con cleafix"]/div[2]/div[1]/div[2]/span/span/a/@href').extract()
            # # print(linkUser)
            i += 1
            yield threadItem
            # yield Request(url=threadItem['thread_link'],callback=self.parse2)  # 抓取当前页数和二级页面数据
	
        print u'第 %s 页共爬取threads %d 条'%(cur_pn,i)



















# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
#丢弃无用的pipline
from scrapy.exceptions import DropItem
from tiebaJieyan.items import threadsItem
import time
import MySQLdb
import MySQLdb.cursors

from scrapy.utils.project import get_project_settings
from tiebaJieyan.common.logger import Logger
from scrapy import log
loger = Logger('threadsPipeline','threadsPipeline.log')
#载入设置
SETTINGS = get_project_settings()

class threadsPipeline(object):

    def __init__(self):
        #数据库链接操作
        self.dbpool = adbapi.ConnectionPool('MySQLdb',
                                            host=SETTINGS['DB_HOST'],
                                            user=SETTINGS['DB_USER'],
                                            passwd=SETTINGS['DB_PASSWD'],
                                            port=SETTINGS['DB_PORT'],
                                            db=SETTINGS['DB_DB'],
                                            charset='utf8',
                                            use_unicode=True,
                                            cursorclass=MySQLdb.cursors.DictCursor)

    def spider_closed(self, spider):
        """ Cleanup function, called after crawing has finished to close open
            objects.
            Close ConnectionPool. """
        self.dbpool.close()

    def process_item(self, item, spider):
        # run db query in thread pool
        #判断不同的item
        if isinstance(item,threadsItem):
            query = self.dbpool.runInteraction(self._conditional_insert, item)
            query.addErrback(self.handle_error)
            return item
        


    def _conditional_insert(self, tx, item):
        # create record if doesn't exist.
        # all this block run on it's own thread
        #用于插入表情
        sql1 = 'set names utf8mb4'
        tx.execute(sql1)
        try:
				args = (item['thread_id'],
                        item['title'],
                        item['author_id'],
                        item['author_name'],
                        item['rep_num'],
                        item['thread_link'],
                        item['is_good'],
                        0,
                        item['c_time']
                        )

                sql = "insert into threads(thread_id,title,author_id,author_name,rep_num,thread_link,is_good,is_top,c_time) VALUES(%s,'%s','%s','%s',%d,'%s',%d,%d,'%s')"%args
                
                try:
				#执行插入操作
                    tx.execute(sql)
					log.msg("Item stored in db: %s" % item, level=log.INFO)
                except MySQLdb.ProgrammingError, e:  
                    loger.error(e)                
                    loger.error(u'insert failed,ProgrammingError:%s'%item)
                except MySQLdb.OperationalError,e:
                    loger.error(e)
                    loger.error(u'insert failed,OperationalError:%s'%item)
				except MySQLdb.DatabaseError,e:
					loger.warning(e)
					 #避免重复存储
					# log.msg("threads_id already stored in db: %s" % item, level=log.WARNING)
					#更新帖子信息
					args = (item['rep_num'],                       
							item['is_good'],
							item['thread_id']
							)
					#sql后面
					sql2 = "UPDATE threads SET rep_num='%s', is_good=%d WHERE thread_id='%s'"%args
					# print sql
					#执行更新操作
					tx.execute(sql2)
					log.msg("update item : %s" % item, level=log.WARNING)
					

        #未爬去id，删除该item
        except KeyError:
            loger.error(u'error item:%s'%item)
            raise DropItem(u'error item:%s'%item)


    def handle_error(self,e):
		log.err(e)

   

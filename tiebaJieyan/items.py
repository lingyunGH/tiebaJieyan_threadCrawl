# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class threadsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    author_id = Field()
    author_name = Field()
    thread_id = Field()
    rep_num = Field()
    is_good = Field()
    # is_top = Field()
    thread_link = Field()
    c_time = Field()
    pass


    


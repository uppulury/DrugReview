# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class DrugreviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Drug_Name = scrapy.Field()
    Drug_Class = scrapy.Field()
    FDA_Alerts = scrapy.Field()
    NReviews = scrapy.Field()
    Drug_Interactions = scrapy.Field()
    Condition = scrapy.Field()
    Comment = scrapy.Field()
    UserRating = scrapy.Field()
    Useful_Reviews = scrapy.Field()
    Date = scrapy.Field()
    Duration = scrapy.Field()
    # CNumber = scrapy.Field()

    pass

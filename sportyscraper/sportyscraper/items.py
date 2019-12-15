# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Spot(scrapy.Item):
    id = scrapy.Field(serializer=int)
    label = scrapy.Field(serializer=str)
    description = scrapy.Field(serializer=str)
    lat = scrapy.Field()
    lng = scrapy.Field()
    sports = scrapy.Field(default=[])
    images = scrapy.Field(default=[])
    attributes = scrapy.Field()

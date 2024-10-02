# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    budget = scrapy.Field()
    posted_time = scrapy.Field()
    skills = scrapy.Field()
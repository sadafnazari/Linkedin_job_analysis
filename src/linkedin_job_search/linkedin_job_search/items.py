# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinJobSearchItem(scrapy.Item):
    date_posted = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    seniority_level = scrapy.Field()
    employment_type = scrapy.Field()
    job_function = scrapy.Field()
    industries = scrapy.Field()
    description = scrapy.Field()
    job_url = scrapy.Field()

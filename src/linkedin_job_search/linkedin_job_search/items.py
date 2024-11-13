# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinJobSearchItem(scrapy.Item):
    """
    A Scrapy item that represents a LinkedIn job post information.

    Attributes:
        date_posted (scrapy.Field): The date when the job was posted.
        title (scrapy.Field): The job title or position name.
        company (scrapy.Field): The name of the company posting the job.
        location (scrapy.Field): The geographical location of the job.
        seniority_level (scrapy.Field): The required experience level for the job.
        employment_type (scrapy.Field): The type of employment.
        job_function (scrapy.Field): The functional area or role of the job.
        industries (scrapy.Field): The industries associated with the job.
        description (scrapy.Field): A detailed description of the job and its responsibilities.
        job_url (scrapy.Field): The URL of the job posting on LinkedIn.
    """

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

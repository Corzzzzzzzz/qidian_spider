# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    article_id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    article_type = scrapy.Field()
    subtypes = scrapy.Field()
    status = scrapy.Field()
    tags = scrapy.Field()
    intro = scrapy.Field()
    words_count = scrapy.Field()
    total_click = scrapy.Field()
    weekly_click = scrapy.Field()
    total_recommend = scrapy.Field()
    weekly_recommend = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    book_intro = scrapy.Field()
    chapter_count = scrapy.Field()
    honors = scrapy.Field()
    url = scrapy.Field()


class PageItem(scrapy.Item):
    page = scrapy.Field()
    article_count = scrapy.Field()


class ErrorItem(scrapy.Item):
    url = scrapy.Field()
    error = scrapy.Field()
    page = scrapy.Field()


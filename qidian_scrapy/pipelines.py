# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from pymysql import cursors
import csv
import datetime
from .items import ArticleItem, PageItem, ErrorItem


class QidianScrapyPipeline(object):
    def __init__(self):
        sql_args = {
            'host': '127.0.0.1',
            'user': 'your MySQL user',
            'password': 'your MySQL user',
            'port': 3306,
            'database': 'qidian',
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        self.dbpool = adbapi.ConnectionPool('pymysql', **sql_args)
        self._sql = '''
        insert into article(article_id, title, author, article_type, subtypes, status, tags, intro, words_count, total_click, weekly_click, total_recommend, weekly_recommend, rating, rating_count, book_intro, chapter_count, honors, url) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        self.fp = open('errorlog.txt', 'a', encoding='utf-8')
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fp.write('\nSpider start at: {}'.format(time))
        self.page_msg = open(r'msg\page.txt', 'a', encoding='utf-8')
        self.error_msg = open(r'msg\error.txt', 'a', encoding='utf-8')

    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            defer = self.dbpool.runInteraction(self._insert_item, item)
            defer.addErrback(self._handle_error, item, spider)
        elif isinstance(item, PageItem):
            print('<Page:{}> item {}'.format(item['page'], item['article_count']))
            self.page_msg.write('<Page:{}> item {} \n'.format(item['page'], item['article_count']))
        elif isinstance(item, ErrorItem):
            print('<Error at page {}> url:{}  \n {}'.format(item['page'], item['url'], item['error']))
            self.error_msg.write('<Error at page {}> url:{}  \n {} \n\n'.format(item['page'], item['url'], item['error']))
        return item

    def close_spider(self, spider):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fp.write('Spider end at: {}\n'.format(time))
        self.fp.close()
        self.page_msg.close()
        self.error_msg.close()

    def _insert_item(self, cursor, item):
        cursor.execute(self._sql, (item['article_id'], item['title'], item['author'], item['article_type'], item['subtypes'], item['status'], item['tags'], item['intro'], item['words_count'], item['total_click'], item['weekly_click'], item['total_recommend'], item['weekly_recommend'], item['rating'], item['rating_count'], item['book_intro'], item['chapter_count'], item['honors'], item['url']))

    def _handle_error(self, error, item, spider):
        self.fp.write('\n <error time>:{} \n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.fp.write('<error msg>:{}\n'.format(error))
        self.fp.write('<error book>{}:{}\n\n'.format(item['title'], item['url']))

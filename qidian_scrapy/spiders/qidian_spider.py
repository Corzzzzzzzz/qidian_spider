# -*- coding: utf-8 -*-
import scrapy
import time
import re
import requests
from scrapy.http.response.html import HtmlResponse
from ..items import ArticleItem, PageItem, ErrorItem
from fontTools.ttLib import TTFont
import time
from io import BytesIO  #StringIO就是在内存中创建的file-like Object，常用作临时缓冲


class QidianSpiderSpider(scrapy.Spider):
    name = 'qidian_spider'
    allowed_domains = ['qidian.com']
    start_urls = ['https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=5657']
    transfer_index = {
        'zero': '0',
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',
        'period': '.'
    }

    def parse(self, response):
        book_items = response.xpath('//ul[contains(@class, "all-img-list")]/li')
        page = re.search(r'page=(\d+)', response.url).group(1)
        article_count = 0
        # 爬取小说详情信息
        for book_item in book_items:
            detail_url = book_item.xpath('.//h4/a/@href').get()
            time.sleep(.5)
            yield response.follow(detail_url, callback=self.parse_article, meta={'page': page})
            article_count += 1
        item = PageItem(page=page, article_count=article_count)
        yield item
        # 获取下一页url并对其进行自身回调
        next_page_url = response.xpath('//ul[@class="lbf-pagination-item-list"]/li[last()]/a/@href').get()
        if next_page_url and "www.qidian.com" in next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_article(self, response):
        try:
            text = response.text
            article_id = response.url.split('/')[-1]
            title = response.xpath('//div[contains(@class, "book-info")]/h1/em/text()').get()
            author = response.xpath('//div[contains(@class, "book-info")]/h1/span/a/text()').get()
            article_type, *subtypes = response.xpath('//div[contains(@class, "book-info")]/p[@class="tag"]/a/text()').getall()
            subtypes = ';'.join(subtypes)
            status, *tags = response.xpath('//div[contains(@class, "book-info")]/p[@class="tag"]/span/text()').getall()
            tags = ';'.join(tags)
            intro = response.xpath('//div[contains(@class, "book-info")]/p[@class="intro"]/text()').get()
            # 得到特殊编码的索引表
            url_pattern = re.compile(r'woff.*?url.*?(http.+?ttf).*?', re.DOTALL)
            camp = None
            font_url_search = re.search(url_pattern, text)
            if font_url_search is not None:
                font_url = font_url_search.group(1)
                camp = self._decode_antifont(font_url)
            # 获取累计数据
            words_count, total_click, total_recommend = 0, 0, 0
            total_num_pattern = re.compile(r'<em>.*?</style>.*?<span.*?>(.*?)</.*?<cite>(.*?)<', re.S)
            total_code_list = re.findall(total_num_pattern, text)
            for code in total_code_list:
                if '字' in code[1]:
                    words_count = self._anti_code_transfer(camp, code[0]) * (10000 if '万' in code[1] else 1)
                elif '会员点击' in code[1]:
                    total_click = self._anti_code_transfer(camp, code[0]) * (10000 if '万' in code[1] else 1)
                elif '推荐' in code[1]:
                    total_recommend = self._anti_code_transfer(camp, code[0]) * (10000 if '万' in code[1] else 1)
            # 获取周数据
            weekly_pattern = re.compile(r'&#183;</span>(.*?)<style>.*?</style>.*?<span.*?>(.*?)</span>(.*?)<', re.DOTALL)
            chack_weekly_pattern = re.compile(r'(&#183;</span>.*?</cite>)')
            weekly_code_list2 = re.findall(chack_weekly_pattern, text)
            weekly_click = weekly_recommend = None
            for index, text in enumerate(weekly_code_list2):
                if len(text) > 30:
                    result_list = re.search(weekly_pattern, text).group(1, 2, 3)
                    result = self._anti_code_transfer(camp, result_list[1])
                    if index == 0:
                        weekly_click = result * (10000 if '万' in result_list[2] else 1)
                    if index == 1:
                        weekly_recommend = result * (10000 if '万' in result_list[2] else 1)
                else:
                    if index == 0:
                        weekly_click = 0
                    if index == 1:
                        weekly_recommend = 0
            # 获取评分和评价人数
            rating, rating_count = self._parse_rating(article_id)

            book_intro = '\n'.join(map(lambda x: x.strip(), response.xpath('//div[@class="book-intro"]/p/text()').getall()))
            # 获取章节数
            chapter_count = response.xpath('//span[@id="J-catalogCount"]/text()').get()
            if chapter_count is None:
                chapter_count = self._get_chapter_count(article_id)
            else:
                chapter_count = int(re.sub(r'[()章]', '', chapter_count))
            honor = response.xpath('//li[@id="honor"]/div/strong/text()').get()
            if honor is not None:
                honors = honor + ';' + ';'.join(response.xpath('//li[@id="honor"]/div//dl/dd/text()').getall())
            else:
                honors = '暂无荣誉'
            url = response.url
            item = ArticleItem(
                article_id=article_id,
                title=title,
                author=author,
                article_type=article_type,
                subtypes=subtypes,
                status=status,
                tags=tags,
                intro=intro,
                words_count=words_count,
                total_click=total_click,
                weekly_click=weekly_click,
                total_recommend=total_recommend,
                weekly_recommend=weekly_recommend,
                rating=rating,
                rating_count=rating_count,
                book_intro=book_intro,
                chapter_count=chapter_count,
                honors=honors,
                url=url,
            )
            yield item
        except Exception as e:
            item = ErrorItem(url=response.url, error=e, page=response.meta.get('page'))
            yield item


    def _decode_antifont(self, font_url):
        response = requests.get(font_url)
        font = TTFont(BytesIO(response.content))
        cmap = font.getBestCmap()  # 返回unicode cmap字典可用的字体
        font.close()
        return cmap

    def _anti_code_transfer(self, cmap, code):
        subcode_list = filter(lambda x: x != '', code.split(';'))
        num_text_list = map(lambda x: cmap[int(x.replace('&#', ''))], subcode_list)
        num = ''.join(self.transfer_index[num_text] for num_text in num_text_list)
        try:
            num = int(num)
        except ValueError:
            num = float(num)
        return num

    def _parse_rating(self, bookid):
        url = 'https://book.qidian.com/ajax/comment/index'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            '_csrfToken': '',
            'bookId': bookid,
            'pageSize': '1'
        }
        resp = requests.get(url, params, headers=headers)
        result = resp.json()
        return result["data"]['rate'], result["data"]['userCount']

    def _get_chapter_count(self, bookid):
        url = 'https://book.qidian.com/ajax/book/category'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        params = {
            '_csrfToken': '',
            'bookId': bookid,
        }
        resp = requests.get(url, params, headers=headers)
        chapter_count = resp.json()['data']['chapterTotalCnt']
        return chapter_count

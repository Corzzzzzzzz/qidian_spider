from scrapy import cmdline


cmdline.execute('scrapy crawl qidian_spider'.split())
# cmdline.execute('scrapy crawl qidian_spider -s JOBDIR=remain/001'.split())
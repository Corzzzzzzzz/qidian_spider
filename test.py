import requests
import re


with open('error_url2.txt', 'a', encoding='utf-8') as inter:
    with open('11.txt', 'r', encoding='GBK') as outer:
        while True:
            line = outer.readline()
            url = re.search(r'https://book.qidian.com/info/[\d]+', line)
            if url is not None:
                inter.write(url.group() + '\n')
                print(url.group())


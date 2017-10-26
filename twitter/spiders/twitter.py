import scrapy
import requests
from datetime import datetime
import csv
import re
from itertools import groupby
import collections

data = open('/home/webdev/workspace/python_scrapy/twitter/twitter/spiders/username.csv', 'r')
screennames = []
for row in data:
    if '\n' in row:
        screenname = row.replace('\n', '')
        screennames.append(screenname)
is_empty = lambda x, y=None: x[0] if x else y

class TwitterAccountItem(scrapy.Item):
    # define the fields for your item here like:
    Username = scrapy.Field()
    Birthday = scrapy.Field()
    # Popularday = scrapy.Field()
    Eachcollected = scrapy.Field()

class TwitterAccountSpider(scrapy.Spider):

    name = 'twitter'
    allowed_domains = ["twitter.com"]
    start_urls = ['https://twitter.com/search-home']
    # start_urls = ['https://twitter.com/search?f=tweets&q=to%3AActor_Vivek%20happy%20birthday%20-wish%20-can%20-me%20-my%20-friend&src=typd']
    # start_urls = ['https://twitter.com/search?f=tweets&vertical=default&q=to:FelipePelaez%20happy%20birthday%20-wish%20-can%20-me%20-my%20-friend&src=typd%3E%20(referer:%20https:/twitter.com/search?f=tweets&q=to%3AActor_Vivek%20happy%20birthday%20-wish%20-can%20-me%20-my%20-friend&src=typd']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/41.0.2228.0 Safari/537.36', }


    def __init__(self, *args, **kwargs):
        super(TwitterAccountSpider, self).__init__(site_name=self.allowed_domains[0], *args, **kwargs)
        self.current_page = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_search_page, headers=self.headers)

    def parse_search_page(self, response):
        search_urls = []
        for screenname in screennames:
            search_name = 'https://twitter.com/search?f=tweets&vertical=default&q=to:' + screenname + ' happy birthday -wish -can -me -my -friend -please -send&src=typd'
            search_urls.append(search_name)
        for search_url in search_urls:
            yield scrapy.Request(url=search_url, callback=self.parse_accounts_item, headers=self.headers)
    def parse_accounts_item(self, response):

        Account = TwitterAccountItem()
        birthday_lists1 = []
        birthday_lists2 = []
        birthday_lists3 = []
        birthday_list = []
        birthday_result_list = []
        today = []

        string_include_name = response.xpath("//div[@class='SearchNavigation-textContainer']//h1/text()").extract()
        if string_include_name:
            username = re.search('to:(.*?)happy', string_include_name[0]).group(1).strip()


        # if string_include_name:
        #     if 'to:' in string_include_name:
        #         string_removed_to = string_include_name.replace('to', '')
        #         username.append(string_removed_to)

        birthday_list = response.xpath("//a[contains(@class, 'tweet-timestamp')]//span[1]/text()").extract()
        for birthday in birthday_list:
            if len(birthday.split()) == 3:
                birthday_lists1.append(birthday)
            elif len(birthday.split()) == 2:
                birthday_lists2.append(birthday)
            else:birthday_lists3.append(birthday)
        if birthday_lists1:
            dates_list1 = [datetime.strptime(date, '%d %b %Y').date() for date in birthday_lists1]
            for date in dates_list1:
                date_list1 = '-'.join(str(date).split('-')[1:])
                birthday_result_list.append(date_list1)
                # '-'.join(str(birthday_num1[0]).split('-')[1:])
        # if birthday_num1:
        #     for date in birthday_num1:
        #         # if len(date) > 5:
        #         #     date = date[:(0,5)]
        #         #     birthday_repeat.append(date)
        #         return
        if birthday_lists2:
            dates_list2 = [datetime.strptime(date, '%b %d').date() for date in birthday_lists2]
            for date in dates_list2:
                date_list2 = '-'.join(str(date).split('-')[1:])
                birthday_result_list.append(date_list2)
        if birthday_lists3:
            today_date_list = [datetime.today().strftime("%Y-%m-%d") for date in birthday_lists3]
            for today_date in today_date_list:
                today_date_list = '-'.join(str(today_date).split('-')[1:])
                birthday_result_list.append(today_date_list)
            #     date_list3 = '-'.join(str(date).split('-')[1:])
            #     birthday_result_list.append(dates_list3)

        # repeat_count = [len(list(group)) for key, group in groupby(birthday_result_list)]
        counter = collections.Counter(birthday_result_list)

        if len(counter) == 0:
            Account['Username'] = username
            Account['Birthday'] = ''
            Account['Eachcollected'] = ''
        else:
            birthday = counter.most_common()[0][0]
            eachcollected = counter.most_common()

        Account['Username'] = username
        Account['Birthday'] = birthday
        Account['Eachcollected'] = eachcollected


        return Account
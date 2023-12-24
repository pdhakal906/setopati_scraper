import scrapy
import re
from config import categories
import json


class NewscraperSpider(scrapy.Spider):
    name = "newscraper"
    allowed_domains = ["setopati.com"]

    # read the data file
    try:
        with open('setopati_news.json', 'r', encoding='utf-8') as file:
            data_list = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        data_list = []

    # start request for each category
    def start_requests(self):
        # yield scrapy.Request("https://www.setopati.com/politics?page=1577", meta={'news_cat': "Politics"})
        for indv_category in categories:
            # yield scrapy.Request(f"https://setopati.com/{indv_category}", callback=self.parse, meta={'news_cat': indv_category})
            yield scrapy.Request(f"https://setopati.com/{indv_category}", callback=self.parse, meta={'news_cat': indv_category})

    # helper function: extracts date using regex
    def extract_date(self, text):
        date_pattern = re.compile(r'प्रकाशित मिति: (.+?)$')
        match = re.search(date_pattern, text)
        if match:
            date = match.group(1)
            return date

    def parse(self, response):
        # look for next page button
        next = response.css("a[rel='next']::attr(href)").get()
        # access category
        news_cat = response.meta['news_cat']

        # look for all 'a' tags and match the specified patterns to extract relevent news links
        links = response.css('a')
        pattern = re.compile(
            r'https://www\.setopati\.com/(exclusive|banking|politics|social|kinmel|sports|nepali-brand|art|global|ghumphir|opinion|blog|cover-story)/\.*')

        for indv_link in links:
            href = indv_link.css("::attr(href)").get()
            if pattern.match(href):
                # check for duplicates
                found = any(item['link'] == href for item in self.data_list)
                # if the link is not stored already in the json file then proceed furthur
                if not found:
                    yield response.follow(href, callback=self.parse_news, meta={'href': href, 'news_cat': news_cat})

        # go to next page untill next variable is not available
        if next is not None:
            yield response.follow(next, callback=self.parse, meta={'news_cat': news_cat})

    def parse_news(self, response):
        details = []
        images = []
        # access news category from meta passed above
        news_cat = response.meta['news_cat']
        title = response.css('h1.news-big-title::text').get()
        author_name = response.xpath(
            '//div[@class="row authors-box"]//h2[@class="main-title"]/a/text()').get()
        author_link = response.xpath(
            '//div[@class="row authors-box"]//h2[@class="main-title"]/a/@href').get()
        published_date = response.css(
            'span.pub-date::text').get()
        # multiple selectors are used because pages are not consistently formatted
        detail = response.css('p::text') or response.css(
            'div.editor-box p::text') or response.css('div.editor-box::text') or response.css('div[style]::text') or response.css('div.editor-box p[style]::text')
        for text in detail:
            details.append(text.get())

        main_image = response.css(
            'div#featured-images img::attr(src)').get()
        images.append(main_image)

        other_image = response.css('div.editor-box p img')
        if other_image:
            for img in other_image:
                images.append(img.css('::attr(src)').get())

        # separate logic to parse old news
        if title is None and author_name is None and published_date is None:
            new_links = response.css('a')
            pattern = re.compile(r'https://www\.setopati\.com/(new-news)/\.*')
            for link in new_links:
                href = link.css("::attr(href)").get()
                if pattern.match(href):
                    # check if link already exists in json file
                    found = any(item['link'] ==
                                href for item in self.data_list)
                    if not found:
                        yield response.follow(href, callback=self.parse_old_news, meta={'href': href, 'news_cat': news_cat})
        else:
            scraped_data = {
                "link": response.meta['href'],
                'news_cat': news_cat.capitalize(),
                "title": title,
                "author": author_name.strip(),
                "author_link": author_link,
                "published_date": self.extract_date(published_date),
                "paragraphs": details,
                "images": images
            }

            self.data_list.append(scraped_data)

            yield scraped_data

    # separate parsing for old news
    def parse_old_news(self, response):
        details = []
        images = []
        news_cat = response.meta['news_cat']
        title = response.css('h1.news-big-title::text').get()
        author_name = response.xpath(
            '//div[@class="row authors-box"]//h2[@class="main-title"]/a/text()').get()
        author_link = response.xpath(
            '//div[@class="row authors-box"]//h2[@class="main-title"]/a/@href').get()
        published_date = response.css(
            'span.pub-date::text').get()

        detail = response.css(
            'div.editor-box p::text') or response.css('div.editor-box::text') or response.css('p::text') or response.css('div[style]::text') or response.css('div.editor-box p[style]::text')

        for text in detail:
            details.append(text.get())

        main_image = response.css(
            'div#featured-images img::attr(src)').get()
        images.append(main_image)

        other_image = response.css('div.editor-box p img')
        if other_image:
            for img in other_image:
                images.append(img.css('::attr(src)').get())

        scraped_data = {
            "link": response.meta['href'],
            "news_cat": news_cat.capitalize(),
            "title": title,
            "author": author_name,
            "author_link": author_link,
            "published_date": self.extract_date(published_date),
            "paragraphs": details,
            "images": images
        }

        self.data_list.append(scraped_data)
        yield scraped_data

    # write data
    def closed(self, reason):
        with open('setopati_news.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.data_list, json_file, ensure_ascii=False, indent=4)

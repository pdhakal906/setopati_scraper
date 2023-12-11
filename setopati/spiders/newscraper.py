import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
import re


class NewscraperSpider(scrapy.Spider):
    name = "newscraper"
    allowed_domains = ["www.setopati.com"]
    start_urls = ["https://www.setopati.com/"]

    def parse(self, response):
        links = response.css('a')
        pattern = re.compile(
            r'https://www\.setopati\.com/(banking|politics|social|kinmel|sports|nepali-brand|art|global|ghumphir)/\.*')

        for link in links:
            href = link.css("::attr(href)").get()
            if pattern.match(href):
                yield response.follow(href, callback=self.parse_news, meta={'href': href})

    def parse_news(self, response):
        details = ""
        images = []
        title = response.css('h1.news-big-title::text').get()
        author_name = response.xpath(
            '//div[@class="row authors-box"]//h2[@class="main-title"]/a/text()').get()
        published_date = response.css(
            'span.pub-date::text').get()

        detail = response.css('p::text')
        for text in detail:
            details += text.get()

        main_image = response.css(
            'div#featured-images img::attr(src)').get()
        images.append(main_image)

        other_image = response.css('div.editor-box p img')
        if other_image:
            for img in other_image:
                images.append(img.css('::attr(src)').get())

        yield {
            "link": response.meta['href'],
            "title": title,
            "author": author_name,
            "published_date": published_date,
            "detail": details,
            "images": images
        }

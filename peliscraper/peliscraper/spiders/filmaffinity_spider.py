# -*- coding= utf-8 -*-
import scrapy

from peliscraper.items import PeliscraperItem


class FilmaffinitySpider(scrapy.Spider):
    name = "filmaffinity"
    allowed_domains = ["filmaffinity.com"]
    start_urls = ["http://www.filmaffinity.com/es/rdcat.php?id=new_th_es"]

    def parse(self, response):
        for node in response.xpath('//div[@id="main-wrapper-rdcat"]'):
            date = None

            first_date_array = node.xpath('div[@class="rdate-cat rdate-cat-first"]/text()')
            if first_date_array:
                date = first_date_array.extract()[0]

            else:
                date_array = node.xpath('div[@class="rdate-cat"]/text()')
                if date_array:
                    date = date_array.extract()[0]

            # We need a date, anyway
            if not date:
                continue

            item = PeliscraperItem()

            item['movie_release_date'] = date

            yield item

# -*- coding= utf-8 -*-
import scrapy

from peliscraper.items import PeliscraperItem


class FilmaffinitySpider(scrapy.Spider):
    name = "filmaffinity"
    allowed_domains = ["filmaffinity.com"]
    start_urls = ["http://www.filmaffinity.com/es/rdcat.php?id=new_th_es"]

    def parse(self, response):
        items = []
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

            #Each movie released on that date
            for movie_node in node.xpath('div[@class="padding-list fa-shadow"]').xpath('div[@class="movie-card movie-card-1"]'):


                movie_release_date = date

                # Movie id
                movie_id_array = movie_node.xpath('@data-movie-id').extract()
                if not movie_id_array or not isinstance(movie_id_array, list) or len(movie_id_array) <= 0:
                    continue

                movie_id = movie_id_array[0]

                # Follow the link to get the rest of the information
                movie_link_array = movie_node.xpath('div[@class="mc-info-container"]').xpath('div[@class="mc-title"]/a/@href').extract()
                if not movie_link_array or not isinstance(movie_link_array, list) or len(movie_link_array) <= 0:
                    continue

                movie_link = movie_link_array[0]

                # Build item object with collected values
                item = PeliscraperItem()

                item['movie_release_date'] = movie_release_date
                item['movie_id'] = movie_id

                items.append(item)

        print items

# -*- coding= utf-8 -*-
import scrapy
import re

from peliscraper.items import PeliscraperItem


class FilmaffinitySpider(scrapy.Spider):
    name = "filmaffinity"
    allowed_domains = ["filmaffinity.com"]
    start_urls = ["http://www.filmaffinity.com/es/rdcat.php?id=new_th_es"]

    def parse(self, response):
        for node in response.xpath('//div[@id="main-wrapper-rdcat"]'):

            for movie_node in node.xpath('div[@class="padding-list fa-shadow"]').xpath('div[@class="movie-card movie-card-1"]'):

                # Follow the link to get the information from the movie's page
                movie_link_array = movie_node.xpath('div[@class="mc-info-container"]').xpath('div[@class="mc-title"]/a/@href').extract()
                if not movie_link_array or not isinstance(movie_link_array, list) or len(movie_link_array) <= 0:
                    continue

                movie_link = movie_link_array[0]

                url = response.urljoin(movie_link)

                yield scrapy.Request(url, callback=self.parse_dir_contents)



    def parse_dir_contents(self, response):

        # Movie id
        # TODO: Extract id from here. Use regular expresion
        movie_id_array = response.xpath('//head/meta[@property="og:url"]/@content').extract()
        if not movie_id_array or not isinstance(movie_id_array, list) or len(movie_id_array) <= 0:
            yield None

        found = re.search('http://www.filmaffinity.com/es/film(.+?).html', str(movie_id_array[0]))
        if found:
            movie_id = found.group(1)

        # Movie release date
        movie_release_date_array = response.xpath('//div[@id="movie-categories"]/text()').re('\((.+?)\)')
        if not movie_release_date_array or not isinstance(movie_release_date_array, list) or len(movie_release_date_array) <= 0:
            yield None

        movie_release_date = movie_release_date_array[0]

        # Movie title
        movie_title_array = response.xpath('//h1[@id="main-title"]').xpath('span[@itemprop="name"]/text()').extract()
        if not movie_title_array or not isinstance(movie_title_array, list) or len(movie_title_array) <= 0:
            yield None
        movie_title = movie_title_array[0].strip()

        # Rest of fields
        dt_nodes = response.xpath('//div[@id="left-column"]/dl[@class="movie-info"]/dt')

        for dt_node in dt_nodes:
            if dt_node.xpath('text()')[0].extract().strip() == u'Título original':
                movie_original_title = dt_node.xpath('following-sibling::dd/text()')[0].extract().strip()
            elif dt_node.xpath('text()')[0].extract().strip() == u'Año':
                movie_year = dt_node.xpath('following-sibling::dd/text()')[0].extract().strip()
            elif dt_node.xpath('text()')[0].extract().strip() == u'Duración':
                movie_runtime = dt_node.xpath('following-sibling::dd/text()')[0].extract().strip()
            elif dt_node.xpath('text()')[0].extract().strip() == u'País':
                movie_country = dt_node.xpath('following-sibling::dd/text()')[0].extract().strip()
            elif dt_node.xpath('text()')[0].extract().strip() == u'Sinopsis':
                movie_plot = dt_node.xpath('following-sibling::dd/text()')[0].extract().strip()



        # Now, build the item
        item = PeliscraperItem()

        item['movie_id'] = movie_id
        item['movie_release_date'] = movie_release_date
        item['movie_title'] = unicode(movie_title)
        item['movie_original_title'] = unicode(movie_original_title)
        item['movie_year'] = unicode(movie_year)
        item['movie_runtime'] = unicode(movie_runtime)
        item['movie_country'] = unicode(movie_country)
        item['movie_plot'] = unicode(movie_plot)


        yield item

# -*- coding= utf-8 -*-
import scrapy
import urllib
import json
from datetime import datetime

from peliscraper.items import PeliscraperItem

IMDB_API_URL = 'http://www.omdbapi.com/?'


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
        movie_id_array = response.xpath('//head/meta[@property="og:url"]/@content').re('http://www.filmaffinity.com/es/film(.+?).html')
        if not movie_id_array or not isinstance(movie_id_array, list) or len(movie_id_array) <= 0:
            yield None

        movie_id = movie_id_array[0].strip()

        # Movie release date
        movie_release_date_array = response.xpath('//div[@id="movie-categories"]/text()').re('\((.+?)\)')
        if not movie_release_date_array or not isinstance(movie_release_date_array, list) or len(movie_release_date_array) <= 0:
            yield None

        movie_release_date = movie_release_date_array[0].strip()

        # Movie rating filmaffinity
        movie_rating_array = response.xpath('//div[@id="movie-rat-avg"]/text()').extract()
        if not movie_rating_array or not isinstance(movie_rating_array, list) or len(movie_rating_array) <= 0:
            yield None

        movie_rating_fa = movie_rating_array[0].strip()

        # Movie title
        movie_title_array = response.xpath('//h1[@id="main-title"]').xpath('span[@itemprop="name"]/text()').extract()
        if not movie_title_array or not isinstance(movie_title_array, list) or len(movie_title_array) <= 0:
            yield None

        movie_title = movie_title_array[0].strip()

        # Movie image link
        movie_poster_link_array = response.xpath('//div[@id="movie-main-image-container"]/a/img/@src').extract()
        if not movie_poster_link_array or not isinstance(movie_poster_link_array, list) or len(movie_poster_link_array) <= 0:
            yield None

        movie_poster_link = movie_poster_link_array[0].strip()

        # Movie web
        movie_official_web_array = response.xpath('//dd[@class="web-url"]/a/@href').extract()
        if movie_official_web_array and isinstance(movie_official_web_array, list) and len(movie_official_web_array) > 0:
            movie_official_web  = movie_official_web_array[0]
        else:
            movie_official_web = u''

        movie_original_title, movie_year, movie_runtime, movie_country, movie_plot, movie_imdb_rating = u'', u'', u'', u'', u'', u''

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

        # The imdb rating
        if movie_original_title:
            query_parameters = {'t': movie_original_title.encode('utf-8')}
            r = urllib.urlopen(IMDB_API_URL + urllib.urlencode(query_parameters))
            data_imdb = json.load(r)

            if data_imdb['Response'].title() == 'True':
                movie_imdb_rating = data_imdb['imdbRating']

        # Transform the date
        try:
            us_date = datetime.strptime(movie_release_date, "%d/%m/%Y").date()
            movie_release_date = us_date.strftime("%Y-%m-%d")
        except ValueError:
            yield None

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
        item['movie_rating_fa'] = unicode(movie_rating_fa)
        item['movie_rating_imdb'] = unicode(movie_imdb_rating)
        item['movie_poster_link'] = movie_poster_link
        item['movie_official_web'] = unicode(movie_official_web)


        yield item

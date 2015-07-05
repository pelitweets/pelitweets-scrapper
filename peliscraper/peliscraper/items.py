# -*- coding= utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in=
# http=//doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PeliscraperItem(scrapy.Item):
    # define the fields for your item here like=
    # name = scrapy.Field()
    movie_id = scrapy.Field()
    movie_title = scrapy.Field()
    movie_original_title = scrapy.Field()
    movie_runtime = scrapy.Field()
    movie_plot = scrapy.Field()
    movie_year = scrapy.Field()
    movie_release_date = scrapy.Field()
    movie_country = scrapy.Field()
    movie_rating_fa = scrapy.Field()
    movie_rating_imdb = scrapy.Field()
    movie_official_web = scrapy.Field()
    movie_poster_link = scrapy.Field()

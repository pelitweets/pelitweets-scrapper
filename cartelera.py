# -*- coding: utf8 -*-
# Jorge Arevalo - jorgeas80@gmail.com

'''
Scrapping the filmaffinity para obtener peliculas en cartelera y almacenarlas en MongoDB
'''

import scraperwiki
import lxml.html
import re
from datetime import *
import json
import urllib

BASE_URL = "http://www.filmaffinity.com"
date = datetime(MAXYEAR, 1, 1).date()
movie_counter = 0

IMDB_API_URL = 'http://www.omdbapi.com/?'

# Paso 1: Obtener pelis en cartelera (filmaffinity)
html = scraperwiki.scrape("http://www.filmaffinity.com/es/rdcat.php?id=new_th_es")
root = lxml.html.fromstring(html)

# Paso 2: Recorrer la página obteniendo, para cada película en cartelera:
#   - Título
#   - Título original
#   - Año
#   - Fecha de estreno
#   - Duración
#   - País
#   - Web oficial
#   - Resumen del argumento
#   - Nota IMDB
#   - Nota Filmaffinity
#   - URL ficha Filmaffinity
#   - URL cartel
table = root.xpath("/html//table")
content_table = table[1]
rows = content_table.findall("tr")

for row in rows:
    cols = row.findall("td")
    for col in cols:
        first_release_date = row.cssselect("div[class='rdate-cat rdate-cat-first']")
        release_date = row.cssselect("div[class='rdate-cat']")
        content = row.cssselect("div[class='padding-list']")

        # ¿Es esta la fecha?
        if first_release_date or release_date:

            if release_date:
                first_release_date = None
            else:
                release_date = first_release_date

            date_str = release_date[0].text_content()

            date_str = date_str.title().replace("De", "")

            # Lo suyo sería usar el local, pero esto funciona...
            date_str = date_str.title().replace("Enero", "January")
            date_str = date_str.title().replace("Febrero", "February")
            date_str = date_str.title().replace("Marzo", "March")
            date_str = date_str.title().replace("Abril", "April")
            date_str = date_str.title().replace("Mayo", "May")
            date_str = date_str.title().replace("Junio", "June")
            date_str = date_str.title().replace("Julio", "July")
            date_str = date_str.title().replace("Agosto", "August")
            date_str = date_str.title().replace("Septiembre", "September")
            date_str = date_str.title().replace("Octubre", "October")
            date_str = date_str.title().replace("Noviembre", "November")
            date_str = date_str.title().replace("Diciembre", "December")

            # Limpiando
            date_str = re.sub(r"[\t\n\r\f\v]", "", date_str)

            # Construimos el objeto fecha
            try:
                date = datetime.strptime(date_str, "%d %B %Y").date()
            except ValueError, e:
                print e
                continue

        # Si no es la columna de fecha, es la de contenido
        elif content:
            div_info = content[0].cssselect("div[class='mc-info-container']")
            div_title = div_info[0].cssselect("div[class='mc-title']")
            title_and_year = div_title[0].text_content()

            # Limpiar
            title_and_year = re.sub(r"[\t\n\r\f\v]", "", title_and_year)

            # Obtenemos titulo y año por separado
            first_par = title_and_year.rfind("(")
            last_par = title_and_year.rfind(")")
            if first_par == -1 or last_par == -1:
                year = 9999
            else:
                try:
                    year = int(title_and_year[first_par+1:last_par])
                except ValueError, e:
                    year = 9999

            title = title_and_year[:first_par]

            # Enlace a la pagina con la ficha
            movie_link = ""
            movie_id = ""
            #div_info[0].make_links_absolute(base_url="http://www.filmaffinity.com/es/")
            for (element, attribute, link, pos) in div_info[0].iterlinks():
                #link = re.sub(r"[\t\n\r\f\v]", "", link)
                if link.startswith("/es/film"):
                    movie_link = BASE_URL + link
                    break

            pos1 = movie_link.rfind("film") + 4
            pos2 = movie_link.rfind(".html")
            movie_id = movie_link[pos1:pos2]

            info_html = scraperwiki.scrape(movie_link)
            root = lxml.html.fromstring(info_html)

            # Get movie items for movie info page

            movie_info_el = root.cssselect("dl[class='movie-info']")
            movie_items = movie_info_el[0].findall("dd")

            # The pic
            for (element, attribute, link, pos) in root.iterlinks():
                if "large" in link:
                    movie_poster_link = link

            # The rating
            rating_div = root.cssselect("div[id='movie-rat-avg']")
            if rating_div:
                movie_fa_rating = rating_div[0].text_content().strip()
                movie_fa_rating = re.sub(r",", ".", movie_fa_rating)

            for movie_item in movie_items:

                if movie_item.getprevious().text_content() == u"Título original":
                    movie_original_title = movie_item.text_content().strip()

                elif movie_item.getprevious().text_content() == u"Duración":
                    movie_runtime = movie_item.text_content().strip()

                elif movie_item.getprevious().text_content() == u"País":
                    movie_country = movie_item.text_content().strip()

                elif movie_item.getprevious().text_content() == "Web Oficial":
                    movie_official_web = movie_item.text_content().strip()

                elif movie_item.getprevious().text_content() == "Sinopsis":
                    movie_plot = movie_item.text_content().strip()


            # The imdb rating
            query_parameters = {'t' : movie_original_title.encode('utf-8')}
            response = urllib.urlopen(IMDB_API_URL + urllib.urlencode(query_parameters))
            data_imdb = json.load(response)

            if data_imdb['Response'].title() == 'True':
                movie_imdb_rating = data_imdb['imdbRating']

            print "************************"
            print "Movie title: %s" % title
            print "Movie original title: %s" % movie_original_title
            print "Movie runtime: %s" % movie_runtime
            print "Movie plot: %s" % movie_plot
            print "Movie year: %d" % year
            print "Movie release date: %s" % date
            print "Movie country: %s" % movie_country
            print "Movie rating (Filmaffinity): %s" % movie_fa_rating
            print "Movie rating (IMDB): %s" % movie_imdb_rating
            print "Movie official web: %s" % movie_official_web
            print "Movie poster link: %s" % movie_poster_link
            print "************************"
            print

            movie_counter = movie_counter + 1

        else:
            continue


print "%d movies" % movie_counter



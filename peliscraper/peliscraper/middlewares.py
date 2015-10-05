# -*- coding= utf-8 -*-
import requests

class PelitweetsMiddleware(object):

    def process_spider_output(response, result, spider):
        # Run Texalytics after parsing
        r = requests.get('http://pelitweets.herokuapp.com/api/analyze')

        if r.status and r.status.code == 200:
            print 'Analytics thrown'

        else:
            print 'Error running analytics'

        #We don't care
        return result
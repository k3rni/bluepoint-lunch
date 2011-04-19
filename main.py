from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
import jsontemplate
import simplejson as json
from lunch import parse_lunch
from lunchdb import fetch_historic_lunch
import datetime

LUNCH_T = jsontemplate.Template(open('lunch.html.jst').read())

def lunch_key():
    return datetime.date.today().strftime('lunch%Y%m%d')

def cached_fetch_lunch():
    key = lunch_key()
    lunch = memcache.get(key)
    if lunch is None:
        lunch = parse_lunch(fetch("http://4smaki.pl/lunch.xml").content)
        memcache.set(key, lunch)
    return lunch

def format_lunch(lunch):
    return LUNCH_T.expand(lunch)

class MainPage(webapp.RequestHandler):
    def get(self):
        lunch = cached_fetch_lunch()
        self.response.out.write(format_lunch(lunch).encode('utf-8'))

class LunchJson(webapp.RequestHandler):
    def get(self):
        lunch = cached_fetch_lunch()
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json.dumps(lunch))

class HistoricLunch(webapp.RequestHandler):
    def get(self, *args):
        year, month, day = map(int, args)
        try:
            lunch = fetch_historic_lunch(year, month, day)
            self.response.out.write(format_lunch(lunch).encode('utf-8'))
        except ValueError: # nie ma takiego w historii
            self.response.out.write('Brak lanczu w bazie')
            self.response.set_status(404)

class HistoricLunchJson(webapp.RequestHandler):
    def get(self, *args):
        year, month, day = map(int, args)
        try:
            lunch = fetch_historic_lunch(year, month, day)
            self.response.headers.add_header('Content-Type', 'application/json')
            self.response.out.write(json.dumps(lunch))
        except ValueError:
            self.response.out.write('{}')
            self.response.set_status(404)

application = webapp.WSGIApplication([
        ('^/$', MainPage),
        ('^/(\d{4})-(\d{2})-(\d{2})$', HistoricLunch),
        ('^/(\d{4})-(\d{2})-(\d{2}).json$', HistoricLunchJson),
        ('^/lunch.json$', LunchJson),
        ('^/lunch$', MainPage),

    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api.urlfetch import fetch
from google.appengine.api import memcache
from xml.etree import ElementTree as ET
import datetime
import jsontemplate
import simplejson as json

def fetch_lunch():
    #key = datetime.date.today().strftime('lunch_%Y-%m-%d')
    #lunch = memcache.get(key)
    #if lunch is not None:
        #return lunch
    doc = fetch("http://4smaki.pl/lunch.xml")
    lunch = parse_lunch(doc.content)
    #memcache.set(key, lunch, time=86400)
    return lunch

def parse_lunch(data):
    xml = ET.fromstring(data.replace('iso-8859-1', 'utf-8')) # zjebana deklaracja
    items = []
    for item in xml.findall('item'):
        lp, cena, nazwa = [item.attrib[k] for k in ('lp', 'cena', 'nazwa')]
        items.append(dict(cena=cena, nazwa=nazwa))
    return dict(lunch=items)

LUNCH = """
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>
    <table>
    <th>Nazwa</th>
    <th>Cena</th>
    {.repeated section lunch}
        <tr>
            <td>{nazwa}</td>
            <td>{cena}</td>
        </tr>
    {.end}
    </table>
</body>
</html>
"""
LUNCH_T = jsontemplate.Template(LUNCH)

def format_lunch(lunch):
    return LUNCH_T.expand(lunch)

class MainPage(webapp.RequestHandler):
    def get(self):
        lunch = fetch_lunch()
        self.response.out.write(format_lunch(lunch).encode('utf-8'))

class LunchJson(webapp.RequestHandler):
    def get(self):
        lunch = fetch_lunch()
        self.response.headers.add_header('Content-Type', 'application/json')
        self.response.out.write(json.dumps(lunch))

application = webapp.WSGIApplication([
        ('^/$', MainPage),
        ('^/lunch.json$', LunchJson),
        ('^/lunch$', MainPage),

    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

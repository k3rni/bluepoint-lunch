# encoding: utf-8

from xml.etree import ElementTree as ET
import unicodedata

import urllib2

def fetch_lunch():
    #key = datetime.date.today().strftime('lunch_%Y-%m-%d')
    #lunch = memcache.get(key)
    #if lunch is not None:
        #return lunch
    doc = urllib2.urlopen("http://4smaki.pl/lunch.xml").read()
    #memcache.set(key, lunch, time=86400)
    return doc

def allcaps(text):
    if not isinstance(text, unicode):
        text = text.decode('utf-8')
    # Lu = Letter, uppercase
    # Zs = Space separator
    # Po = Punctuation, other
    # Pd = Punctuation, dash
    # Nd = Number, decimal
    # http://www.unicode.org/reports/tr44/tr44-4.html#General_Category_Values
    return all(unicodedata.category(c) in ('Lu', 'Zs', 'Po', 'Pd', 'Nd') for c in text)

def parse_lunch(data):
    xml = ET.fromstring(data.replace('iso-8859-1', 'utf-8')) # zjebana deklaracja
    lunch = dict(combos=[], soup=dict(items=[]), general=dict(items=[]))
    headers_count = 0
    section = None
    for item in xml.findall('item'):
        lp, cena, nazwa = [item.attrib[k] for k in ('lp', 'cena', 'nazwa')]
        # Semantyka:
        # wpisy z * na początku nie należą pod żaden nagłówek, wpisy bez wpadają pod ostatni wczytany
        # ostatni head jest o kanapkach, nie ma ceny i w sumie nie wiadomo co z nim zrobić

        # puste linie ignorujemy, obcinamy wszystkie spacje po bokach
        nazwa = nazwa.strip()
        if not nazwa: continue

        # allcaps są nagłówki. pierwszy nagłówek to zawsze MENU $data
        if allcaps(nazwa):
            headers_count += 1
            if headers_count > 1:
                section = dict(title=nazwa, price=cena, items=[])
                lunch['combos'].append(section)
            continue

        # po nagłówku menu są zupy, potem kolejne nagłówki i ich potrawy
        if nazwa.startswith("*"):
            if headers_count == 1:
                lunch['soup']['items'].append(dict(name=nazwa[1:], price=cena))
            else:
                lunch['general']['items'].append(dict(name=nazwa[1:], price=cena))
        else:
            section['items'].append(dict(name=nazwa, price=cena))
            



    return lunch

if __name__ == "__main__":
    import jsontemplate,pprint
    l = parse_lunch(fetch_lunch())
    pprint.pprint(l)
    print jsontemplate.Template(open('lunch.html.jst').read()).expand(l)

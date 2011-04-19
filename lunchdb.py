from google.appengine.ext import db

class LunchMenu(db.Model):
    day = db.DateProperty(required=True)
    menu = db.TextProperty(required=True)

def fetch_historic_lunch(year, month, day):
    raise ValueError("nie ma takiego lanczu!")


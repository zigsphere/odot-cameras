import json
import os
from dateutil import parser
from datetime import datetime
from urllib.parse import quote
import requests
from flask import Flask, render_template, url_for, abort
from flask_caching import Cache

APIKEY = os.getenv('API_KEY')                # Use as environment in compose file
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') # Use as environment in compose file
HOMEPAGE_CACHE_TIMEOUT = int(os.getenv('HOMEPAGE_CACHE_TIMEOUT', '30'))
DATA_CACHE_TIMEOUT = int(os.getenv('DATA_CACHE_TIMEOUT', '900'))

app = Flask(__name__, template_folder='./templates')

config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 180,
    "CACHE_REDIS_HOST": "redis",
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_PASSWORD": REDIS_PASSWORD
}

app.config.from_mapping(config)
cache = Cache(app)

regions = {
  'Roseburg': '-123.813436,42.798917,-123.143353,43.447403',
  'Klamath Falls': '-122.553828,42.140986,-121.602086,42.457756',
  'Ashland / Siskiyou': '-122.819803,42.009244,-122.520011,42.320272',
  'Medford / Central Point': '-123.006094,42.179417,-122.776114,42.508094',
  'Eugene': '-123.235,43.946472,-122.792656,44.226514',
  'Salem / Surrounding Area': '-123.153519,44.819314,-122.649742,45.284286',
  'Portland': '-122.846803,45.312897,-122.378803,45.568083'
}

@app.route('/')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT)
def homepage():
  image_urls, incidents = get_data()
  #print(incidents) # For debugging
  return render_template('index.html', urls=image_urls, incidents=incidents)

@cache.cached(timeout=DATA_CACHE_TIMEOUT, key_prefix='data')
def get_data():
  headers = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': APIKEY
  }
  try:
    image_urls = {
      city: requests.get(f'https://api.odot.state.or.us/tripcheck/Cctv/Inventory?Bounds={quote(coord)}', headers=headers).json()['CCTVInventoryRequest']
      for city, coord in regions.items()
    }

    incidents = {
      city: requests.get(f'https://api.odot.state.or.us/tripcheck/Incidents?Bounds={quote(coord)}', headers=headers).json()['incidents']
      for city, coord in regions.items()
    }
  except requests.exceptions.RequestException:
    abort(500)

  return image_urls, incidents

@app.context_processor
def utility_processor():
    def format_time(isotime):
        dt = parser.parse(isotime)
        formatted_time = dt.strftime("%m/%d/%Y %H:%M")
        return formatted_time
    return dict(format_time=format_time)

@app.route("/ping/")
def ping():
  return "PONG"

@app.errorhandler(500)
def page_exception(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)

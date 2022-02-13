import json
import os
import re
from dateutil import parser
from datetime import datetime
from urllib.parse import quote
from jinja2 import TemplateNotFound
import requests
from flask import Flask, render_template, url_for, abort
from flask_caching import Cache
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__, template_folder='./templates')

clean = re.compile('<.*?>')

APIKEY = os.getenv('API_KEY')                                           # Use as environment in compose file
APIKEY_2 = os.getenv('API_KEY_2')                                       # Use as environment in compose file
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')                            # Use as environment in compose file
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')                           # Use as environment in compose file
HOMEPAGE_CACHE_TIMEOUT = int(os.getenv('HOMEPAGE_CACHE_TIMEOUT', '30')) # Use as environment in compose file
DATA_CACHE_TIMEOUT = int(os.getenv('DATA_CACHE_TIMEOUT', '900'))        # Use as environment in compose file

config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 180,
    "CACHE_REDIS_HOST": REDIS_HOST,
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
  events = get_events()
  #print(incidents) # For debugging
  try:
    return render_template('index.html', urls=image_urls, incidents=incidents, events=events)
  except TemplateNotFound:
    abort(404)

@app.route('/roseburg')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='rbg')
def roseburg():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('roseburg.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/eugene')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='eug')
def eugene():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('eugene.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/klamathfalls')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='lmt')
def klamathfalls():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('klamathfalls.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/ashland')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='ash')
def ashland():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('ashland.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/medford')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='mfr')
def medford():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('medford.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/salem')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='sle')
def salem():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('salem.html', urls=image_urls, incidents=incidents, events=events)

@app.route('/portland')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='pdx')
def portland():
  image_urls, incidents = get_data()
  events = get_events()
  return render_template('portland.html', urls=image_urls, incidents=incidents, events=events)

@cache.cached(timeout=DATA_CACHE_TIMEOUT, key_prefix='data')
def get_data():
  headers = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': APIKEY
  }
  try:
    image_urls = {
      city: get_json(f'https://api.odot.state.or.us/tripcheck/Cctv/Inventory?Bounds={quote(coord)}', headers)['CCTVInventoryRequest']
      for city, coord in regions.items()
    }

    incidents = {
      city: get_json(f'https://api.odot.state.or.us/tripcheck/Incidents?Bounds={quote(coord)}', headers)['incidents']
      for city, coord in regions.items()
    }
  except requests.exceptions.RequestException:
    abort(500)

  return image_urls, incidents

@cache.cached(timeout=DATA_CACHE_TIMEOUT, key_prefix='events')
def get_events():
  headers = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': APIKEY_2
  }
  try:
    events = {
      city: get_json(f'https://api.odot.state.or.us/tripcheck/Tle/Events?Bounds={quote(coord)}', headers)['Incidents']
      for city, coord in regions.items()
    }

  except requests.exceptions.RequestException:
    abort(500)

  return events

def get_json(url, headers):
  """Fetch details for coordinates."""
  resp = requests.get(url, headers=headers)
  try:
    resp.raise_for_status()
  except Exception as e:
    print(f"Error fetching {url}: {e}")
    raise e
  return resp.json()

@app.context_processor
def utility_processor():
  def format_time(isotime):
    dt = parser.parse(isotime)
    formatted_time = dt.strftime("%m/%d/%Y %H:%M")
    return formatted_time
  return dict(format_time=format_time)

@app.context_processor
def tag_processor():
  def remove_tags(text):
    return re.sub(clean, '', text)
  return dict(remove_tags=remove_tags)

@app.route("/ping")
def ping():
  return "PONG"

@app.errorhandler(500)
def page_exception(error):
  return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found_exception(error):
  return render_template('404.html'), 404

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)

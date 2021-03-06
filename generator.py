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

# Scheduler for autoloading page for cache purposes
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv('.env')

app = Flask(__name__, template_folder='./templates')

clean = re.compile('<.*?>')

APIKEY                 = os.getenv('API_KEY')                           # Use as environment in compose file
APIKEY_2               = os.getenv('API_KEY_2')                         # Use as environment in compose file
WEATHER_API_KEY        = os.getenv('WEATHER_API_KEY')                   # Use as environment in compose file https://www.weatherapi.com/
REDIS_PASSWORD         = os.getenv('REDIS_PASSWORD')                    # Use as environment in compose file
REDIS_HOST             = os.getenv('REDIS_HOST', 'redis')               # Use as environment in compose file
HOMEPAGE_CACHE_TIMEOUT = int(os.getenv('HOMEPAGE_CACHE_TIMEOUT', '30')) # Use as environment in compose file
DATA_CACHE_TIMEOUT     = int(os.getenv('DATA_CACHE_TIMEOUT', '900'))    # Use as environment in compose file
LOAD_TIMEOUT           = int(15)                                        # Seconds
RELOAD_REFRESH         = DATA_CACHE_TIMEOUT - LOAD_TIMEOUT

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

zipcodes = {
  'Roseburg': '97470',
  'Klamath Falls': '97601',
  'Ashland': '97520',
  'Medford': '97501',
  'Eugene': '97401',
  'Salem': '97301',
  'Portland': '97035'
}
 
# Function for scheduler to reload pages seconds before the timeout expires
def reload_pages():
  requests.get('http://odot:5000/', timeout=LOAD_TIMEOUT)
  requests.get('http://odot:5000/roseburg', timeout=LOAD_TIMEOUT)
  requests.get('http://odot:5000/klamath', timeout=LOAD_TIMEOUT)

@app.route('/')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT)
def homepage():
  image_urls, incidents = get_data()
  events = get_events()
  weather = get_weather()
  # print(weather) # For debugging
  try:
    return render_template('index.html', urls=image_urls, incidents=incidents, events=events, weather=weather)
  except TemplateNotFound:
    abort(404)

@app.route('/klamath')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='kfalls')
def klamath():
  image_urls, incidents = get_data()
  events = get_events()
  weather = get_weather()
  return render_template('klamath.html', urls=image_urls, incidents=incidents, events=events, weather=weather)

@app.route('/roseburg')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT, key_prefix='rsbg')
def roseburg():
  image_urls, incidents = get_data()
  events = get_events()
  weather = get_weather()
  return render_template('roseburg.html', urls=image_urls, incidents=incidents, events=events, weather=weather)

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

    for cameras in image_urls.values():
      for camera in cameras:
        cctv_url = camera["cctv-url"]
        if cctv_url.startswith("http://"):
          camera["cctv-url"] = cctv_url.replace("http:", "https:", 1)

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

@cache.cached(timeout=DATA_CACHE_TIMEOUT, key_prefix='weather')
def get_weather():
  headers = {
    'Cache-Control': 'no-cache',
  }
  try:
    weather = { 
      city: get_json(f'https://api.weatherapi.com/v1/current.json?key={quote(WEATHER_API_KEY)}&q={quote(zip)}&aqi=no', headers)['current']
      for city, zip in zipcodes.items()
    }

  except requests.exceptions.RequestException:
    abort(500)

  return weather

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

@app.route("/ping/")
def ping():
  return "PONG"

@app.errorhandler(500)
def page_exception(error):
  return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found_exception(error):
  return render_template('404.html'), 404


# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=reload_pages, trigger="interval", seconds=RELOAD_REFRESH)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=False)

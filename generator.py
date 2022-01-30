import json
import os
from urllib.parse import quote
import requests
from flask import Flask, render_template, url_for, jsonify, request
from flask_caching import Cache

APIKEY = os.getenv('API_KEY') # Use as environment in compose file
HOMEPAGE_CACHE_TIMEOUT = int(os.getenv('HOMEPAGE_CACHE_TIMEOUT', '30'))
DATA_CACHE_TIMEOUT = int(os.getenv('DATA_CACHE_TIMEOUT', '900'))

app = Flask(__name__, template_folder='./templates')

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 180
}

app.config.from_mapping(config)
cache = Cache(app)

regions = {
  'Roseburg': '-123.813436,42.798917,-123.143353,43.447403',
  'Klamath Falls': '-122.553828,42.140986,-121.602086,42.457756',
  'Portland': '-122.875228,45.414915,-122.631469,45.559331',
  'Eugene': '-123.235,43.946472,-122.792656,44.226514',
  'Ashland': '-122.819803,42.009244,-122.520011,42.320272'
}

@app.route('/')
@cache.cached(timeout=HOMEPAGE_CACHE_TIMEOUT)
def homepage():
  image_urls, incidents = get_data()
  #print(incidents) To debug
  return render_template('index.html', urls=image_urls, incidents=incidents)

@cache.cached(timeout=DATA_CACHE_TIMEOUT, key_prefix='data')
def get_data():
  headers = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': APIKEY
  }

  image_urls = {
    city: requests.get(f'https://api.odot.state.or.us/tripcheck/Cctv/Inventory?Bounds={quote(coord)}', headers=headers).json()['CCTVInventoryRequest']
    for city, coord in regions.items()
  }

  incidents = {
    city: requests.get(f'https://api.odot.state.or.us/tripcheck/Incidents?Bounds={quote(coord)}', headers=headers).json()['incidents']
    for city, coord in regions.items()
  }

  return image_urls, incidents

@app.route("/ping/")
def ping():
  return "PONG"

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

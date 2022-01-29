import json
import os
from urllib.parse import quote
import requests
from flask import Flask, render_template, url_for

APIKEY = os.getenv('API_KEY') # Use as environment in compose file

app = Flask(__name__, template_folder='./templates')

regions = {
  'Roseburg': '-123.813436,42.798917,-123.143353,43.447403',
  'Klamath Falls': '-122.553828,42.140986,-121.602086,42.457756',
  'Portland': '-122.875228,45.414915,-122.631469,45.559331',
  'Eugene': '-123.235,43.946472,-122.792656,44.226514',
  'Ashland': '-122.819803,42.009244,-122.520011,42.320272'
}

@app.route('/')
def homepage():
  payload={}
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

  #print(incidents) To debug
  return render_template('index.html', urls=image_urls, incidents=incidents)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

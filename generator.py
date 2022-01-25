import json
import os
import requests
from flask import Flask, render_template
from urllib.parse import quote

APIKEY = os.getenv('API_KEY') # Use as environment in compose file

app = Flask(__name__, template_folder='.')

regions = {
  'Roseburg': '-123.813436,42.798917,-123.143353,43.447403',
  'Portland': '-122.875228,45.414915,-122.631469,45.559331',
}

@app.route('/')
def homepage():
  payload={}
  headers = {
    'Cache-Control': 'no-cache',
    'Ocp-Apim-Subscription-Key': f"{APIKEY}"
  }

  responses = [
    requests.get(f'https://api.odot.state.or.us/tripcheck/Cctv/Inventory?Bounds={quote(value)}', headers=headers).json()['CCTVInventoryRequest']
    for value in regions.values()
  ]

  print(responses)
  return render_template('index.html', urls=responses)

if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

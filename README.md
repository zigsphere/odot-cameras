# ODOT Road Conditions
Using the Oregon Department of Transportation (ODOT) CCTV API to generate a site with cameras.

[![Build Status][build_image]][build_page] [![Lint Status][b_image]][b_page] [![CodeQL][ca_image]][ca_page]

[build_image]: https://github.com/zigsphere/odot-cameras/actions/workflows/docker-publish.yml/badge.svg
[build_page]: https://github.com/zigsphere/odot-cameras/actions


[b_image]: https://github.com/zigsphere/odot-cameras/actions/workflows/python-app.yml/badge.svg
[b_page]: https://github.com/zigsphere/odot-cameras/actions

[ca_image]: https://github.com/zigsphere/odot-cameras/actions/workflows/codeql-analysis.yml/badge.svg
[ca_page]: https://github.com/zigsphere/odot-cameras/actions

This is an experimental Flask web application that pulls from the ODOT API. The site shows various cities with the surrounding traffic cameras and incident information.

Site is live at: https://odotcams.josephziegler.dev

### To Run
In the docker-compose.yml file, set the API_KEY environment variable to your own API key. You can get one from https://apiportal.odot.state.or.us/product#product=tripcheck-api-data. Once set:

```
docker-compose up -d
```

For development, in the docker-compose.yml file, comment out the image attribute and uncomment the `build: .`. Then you can simply run `docker-compose up --build` to build the image from the included Dockerfile.

### Caching
The application is currently using Redis to store the cache for the retrieved data from the ODOT API. This is done by using the Flask-Caching Python library. A cache is used to avoid hitting the API rate limit from each load of the page. Instead, the cache is stored for the time specified for HOMEPAGE_CACHE_TIMEOUT and DATA_CACHE_TIMEOUT. These can be set as environment variables for the ODOT container image within the docker-compose file. Now, when the page is loaded by several concurrent connections, the data is pulled from the Redis cache rather than performing an API call each time. You can change the cache type if desired. https://flask-caching.readthedocs.io/ 

### Used APIs
A list of the data that can be retreived is listed [here](https://tripcheck.com/Pages/API); however, currently the [CCTV inventory](https://apiportal.odot.state.or.us/api-details#api=tripcheck-api-v1-0;rev=1&operation=Cls_GetClsInventory) and [incidents](https://apiportal.odot.state.or.us/api-details#api=tripcheck-api-v1-0;rev=1&operation=Inc_GetIncidentsFilter) API are the only two used in this application.

When retreiving API credentials, you will receive two tokens. You will need them both. This application uses multiple keys to avoid the API rate limits due to the amount of data being pulled.

### Environment Variables
Below are the environment variables that can be set:

    - API_KEY                # First API Key
    - API_KEY_2              # Second API Key
    - DATA_CACHE_TIMEOUT     # Cache for the fetched JSON (default is 900 seconds)
    - HOMEPAGE_CACHE_TIMEOUT # Cache for the rendered output (default is 30 seconds)
    - REDIS_HOST             # Redis hostname (default is redis if using the included container)
    - REDIS_PASSWORD         # Redis Password (default is password)

### Planned Features
- [ ] Better web frontend
- [ ] Multi-page site for other cities with more information
- [ ] Better error handling
- [x] Use Redis for cache management (Currently using python dictionaries aka SimpleCache)
- [x] Add local event information for each city
- [ ] Add road & weather information for each city
 
![road](https://github.com/zigsphere/odot-cameras/blob/main/static/road.png?raw=true)

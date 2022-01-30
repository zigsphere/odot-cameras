# ODOT Cameras
Using the Oregon Department of Transportation (ODOT) CCTV API to generate a site with cameras.

[![Build Status][build_image]][build_page] [![Lint Status][b_image]][b_page]

[build_image]: https://github.com/zigsphere/odot-cameras/actions/workflows/docker-publish.yml/badge.svg
[build_page]: https://github.com/zigsphere/odot-cameras/actions


[b_image]: https://github.com/zigsphere/odot-cameras/actions/workflows/python-app.yml/badge.svg
[b_page]: https://github.com/zigsphere/odot-cameras/actions

This is an experimental Flask web application that pulls from the ODOT API. The site shows various cities with the surrounding traffic cameras and incident information.

Site is live at: https://odotcams.josephziegler.dev

### To Run
In the docker-compose.yml file, set the API_KEY environment variable to your own API key. You can get one from https://apiportal.odot.state.or.us/product#product=tripcheck-api-data. Once set:

```
docker-compose up -d
```

For development, in the docker-compose.yml file, comment out the image attribute and uncomment the `build: .`. Then you can simply run `docker-compose up --build` to build the image from the included Dockerfile.

### Used APIs
A list of the data that can be retreived is listed [here](https://tripcheck.com/Pages/API); however, currently the [CCTV inventory](https://apiportal.odot.state.or.us/api-details#api=tripcheck-api-v1-0;rev=1&operation=Cls_GetClsInventory) and [incidents](https://apiportal.odot.state.or.us/api-details#api=tripcheck-api-v1-0;rev=1&operation=Inc_GetIncidentsFilter) API are the only two used in this application.

### Planned Features
 - Better web frontend
 - Multi-page site for other cities with more information
 - Better error handling
 
![road](https://github.com/zigsphere/odot-cameras/blob/main/static/road.png?raw=true)

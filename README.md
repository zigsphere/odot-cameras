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

### Planned features
 - Better web frontend
 - Multi-page site for other cities with more information
 
![road](https://github.com/zigsphere/odot-cameras/blob/main/static/road.png?raw=true)

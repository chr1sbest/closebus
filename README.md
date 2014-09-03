CloseBus
=======

CloseBus gives realtime travel estimates for nearby public transportation.

Why realtime travel estimates?
---
I chose to build out CloseBus for two main reasons:

> 1) I wanted to become more familiar with geolocation and the capabilities of the Google Maps API's.

> 2) The app would be immediately useful to myself and my peers!

Technical Stack Overview
---
I chose to split my time evenly between the frontend and backend as a **full-stack** engineer. The full stack includes a RESTful interface built on Python **Flask**, front end single-page app built with **Backbone.js** and a **Redis** cache. The application is currently deployed to **Heroku** on http://closebus.herokuapp.com.

I chose **Flask** because it is incredibly lightweight and easy to quickly prototype API's and applications in general. Unfortunately, running on CPython, I'm not able to effectively use multi-threading due to the GIL. Flask is my framework of choice for building small projects.

**Backbone.js** was similiarly chosen due its simplicity and due to it being lighter than other front end frameworks. I have been looking forward to learning Angular.js in a new project, but I felt this might not be the time and place.

As most of the data is realtime travel information, there is little reason to write anything to disk. I chose to use **Redis** as a cache to prevent duplicate calls to third party API's (and stay under the rate limit), cache results of web crawling for stop_id's to prevent from having to crawl multiple times, and to give quicker response times to users!

It's super quick and easy (and **free**!) to deploy to **Heroku.**

Backend
====

The backend consists of three main steps

> 1) Finding nearby stop_id's using Google Maps API.

> 2) Querying travel API's for realtime travel estimates using the stop_id.

> 3) Caching results.

Nearby Stops
----

The **/stop_ids** endpoint mainly serves as an adapter to the Google Places API.

I chose to implement the chain of responsibility pattern in this attempt to find stop_id's. Currently, the only strategy is to crawl the Google Places URL (strategy details below), but the app is built to successively try strategies until a stop_id is returned. The app lazily finds new stops (in a radius of the user's marker location) and caches them.

**Crawl Strategy** - Currently, the Google Places API doesn't offer the vital piece of information I need (stop_id), so I had to hack my way around it. The places API returns a URL --> this URL contains information on stop_id in a specific div. Using BeautifulSoup and a little regex, I was able to pull out the stop_ids. This strategy is reliant on companies uploading stop_ids to Google (not always the case!) and reliant on a few more get requests that I'd like. It's not ideal, but it currently gets the job done.

I'm certain that the transit agencies have better data I could use to be able to map some value from the Google Places API directly to a stop_id. In the future, I would look into gaining the official data and use the web crawling as a backup strategy.

Querying Travel API's
-----

The **/departures** endpoint serves as an adapter to transit agencies.

I wrote out an **AbstractAgency* class to hold contractual details for each transit agency class to implement specific methods and return specific data. Each Agency basically needs to make a get request with parameters and translate the response into uniform JSON data that can be used by the frontend.

Currently the only transit agency I have completed is NextBus, although it is very easily extendable. 

Caching
-----

Realtime data is cached on a 60 second TTL, {place: stop_id} is cached ~permanently.

NextBus will rate limit me at 2mb/20s. Each request is around 1kb -- 100 requests a second for 20 seconds would get me rate limited. With requests cached with 60s TTL, I could prevent duplicate requests for realtime travel estimates of a specific stop and theoretically maintain information on a minimum of 2,000 different stops at a time and a maximum of 6,000. 

Mapping places to stop_id's was kind of a big hassle (written above in the crawler strategy), and I felt that it was best to cache these as well. If a user discovers a new bus stop, the bus stop has to jump through a bunch of hoops to discover its stop_id, this is then cached. The next time any user is in vicinity of the bus stop, the stop_id will be returned immediately due to it being cached. As a side effect, this also could encourage users to explore and play with the app!

The cache is written as a decorator that I can easily throw onto RESTful methods (yay Python!)

Frontend
=====

The frontend is super simple and consists of a **MapView** and **RouteViews**. The interface is inspired by Uber and consists of a movable marker and clickable bus stops.

The MapView does most of the heavy lifting in building out the initial page, geolocating, and finding nearby bus stops. When the MapView finds a bus stop, it instantiates a new **StopModel** and adds it to it's **StopCollection.** The StopModel then connects to the **/stop_id** endpoint to try to map the place_id with a stop_id. If successful, a bus stop marker is added onto the map.

When a bus stop marker is clicked, a new RouteView is instantiated. The **RouteModel** attached to this view fetches from the **/departures** endpoint and then parses and attaches a rendered template to the infowindow above the marker.

Improvements
====

There are five main improvements I will be working on in the next week.

> 1) Better automated testing.

> 2) Better display of bus stop data.

> 3) More travel agencies implemented.

> 4) Asynchronous requests to third-party API's.

> 5) Better data from transit agencies.

**Automated Testing**

Due to not being familiar with the capabilities of Google Maps, my process on the frontend consisted mostly of hacking. Had I been more familiar of what I was capable of, I could have written better tests to accompany my code.

Admittedly, testing is where I need the most help. I have felt the pain of refactoring larger apps without proper test coverage, and I don't want to feel it again. I will be spending the next few days focused on writing unit tests for my Javascript frontend and improving my tests on my Flask backend. My process on this app was more of DDT than TDD :\

**Displaying Data**

It currently isn't as mobile-friendly as I would like it to be. I would like to try using a tabbed modal popup to display bus stop information.

**More Agencies**

The backend is built to extend and incorporate new agencies with ease, so why not? I have shown a few friends my app, but it only currently works in Berkeley/Oakland!

**Asynchronous Requests**

If the user is in a location with mulitple new bus stop, there is a consecutive series of long requests that need to take place before stop times can be registered. It should be beneficial to handle these asynchronously.

**Better Data**

I will show my app prototype to NextBus and see if they will give me better data so that I don't have to crawl for stop_ids.

Final Thoughts
=========

I had a lot of fun building this app and I've learned a ton. There is a lot left to implement, but I'm happy with the progress I've made so far!

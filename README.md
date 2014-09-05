CloseBus
=======

CloseBus gives realtime travel estimates for nearby public transportation.

Why realtime travel estimates?
---
I chose to build out CloseBus for two main reasons:

> 1) Gain familiarity with geolocation and the capabilities of the Google Maps API's.

> 2) The app would be immediately useful to myself and my peers!


Current Status
---
- The application is deployed and capable of holding real-time data for up to 6,000 bus stops at a time.
- There is near complete coverage in SF & East Bay, but the coverage in New York City and Los Angeles is mostly restricted to the densely populated areas (Downtown LA, Bronx, Brooklyn, Staten Island.)
- While the application is functional on mobile devices, the application has been optimized for non-mobile usage.

Technical Stack Overview
---
I chose to split my time evenly between the frontend and backend as a **full-stack** engineer. The full stack includes a RESTful interface built on Python **Flask** with a **Redis** cache, and a frontend single-page app built with **Backbone.js**. The application is currently deployed to **Heroku** on http://closebus.herokuapp.com.

I chose **Flask** because it is lightweight and easy to quickly prototype API's and general applications. Unfortunately, running on CPython, I'm not able to effectively utilize multi-threading due to the GIL. Flask is my framework of choice for building small projects.

**Backbone.js** was similiarly chosen due its simplicity and flexibility. I have been looking forward to learning Angular.js in a new project, but I felt this might not be the time and place.

As most of the data is realtime travel information, there is little reason to write anything to disk. I chose to use **Redis** as a cache to prevent duplicate calls to third party API's (and stay under the rate limit) and to have lower latency for users.

I chose to deploy to **Heroku** due to the ease of deployment and cost (free!)

Backend
====

The backend consists of four main components.

> 1) Finding nearby bus stops.

> 2) Finding the corresponding **stop_id** for each stop.

> 2) Using the stop_id to query travel API's for realtime travel estimates.

> 3) Caching results.

Nearby Stops
----

The **/stop_id** endpoint mainly serves as an adapter to the Google Places API.

The frontend picks up **place_id**s for nearby locations and then queries */stop_id/place_id* for each location. This API endpoint simply formats the request to the Google Places API, handles errors, and returns the updated information to the frontend.


Finding the corresponding stop_id for each stop.
----
This was the most challenging and by far the most fun component to work on. The Google Places API doesn't explicity return information on the *stop_id*. However, I was able to manage to find *two* ways around it. Unfortunately, neither method is foolproof, so I decided to employ the chain of command design pattern in an attempt to catch as much as I could.

After unsuccessfully looking for ways to get my hands on official data, I started to doubt the feasability of the project. I played around with the data that was available to me, and I ended up finding something of interest! The GAPI data returned a specific url for each place. This url mapped to a page which, at the very very bottom (in small grey letters), listed Stop ID's. It was terribly inconsistent, but it was something. I wrote a crawler to parse out the data I needed and implemented this time-consuming process to be cached and lazy.

I wasn't too happy with the inconsistencies, but this was the best I could do.. Or so I thought! I luckily stumbled onto some data that mapped cross streets to stop_ids and I wrote a little script to extract it. Unfortunately, each agency that uploads data to Google Maps does so in a different way -- very few of these values mapped to anything in my data. Regex to the rescue! I wrote out a huge block of regex.finds() and regex.subs() that takes care of the majority of inconsistencies. Shoutout to this [Python Regex helper!](https://pythex.org/) The latency isn't anywhere near as bad as the previous crawler strategy, but I still cache these results so that I don't have to read from disk.

Querying Travel API's
-----

The **/departures** endpoint serves as an adapter to transit agencies.

I wrote out an **AbstractAgency** class to hold contractual details for each TransitAgency to implement specific methods and return specific data. Each TransitAgency needs to make a get request with correct parameters and translate the response into uniform JSON data that can be used by the frontend.

Currently the only TransitAgency I have completed is NextBus, although it is very easily extendable. 

Caching
-----

Realtime data is cached on a 60 second TTL. {Place: stop_id} is cached ~permanently.

NextBus will rate limit me at 2mb/20s. With each request around 1kb, making 100 requests a second for 20 seconds would get me rate limited. With requests cached on a 60s TTL, not only do I prevent duplicate requests for realtime travel estimates of a specific stop, but I can theoretically maintain information on a maximum of 6,000 bus stops at a time. 

The mapping of place_id's to stop_id's is cached so that the application doesn't need to go through all the hassle every time a user is within a known stop's vicinity.

The cache is written as a decorator that I can easily throw onto RESTful methods (yay Python!)

Frontend
=====

The frontend consists of a **MapView** and **StopViews** that contain **RouteViews**. The interface is inspired by Uber and consists of a movable marker and clickable bus stops.

The MapView does most of the heavy lifting by building out the initial page, geolocating, and finding nearby bus stops via Google Places API. When the MapView finds a bus stop, it instantiates a new **StopModel** and adds it to it's **StopCollection.** The StopModel then fetches from the **/stop_id** endpoint to attempt to retrieve stop_id details. If successful, a bus stop marker is added onto the map.

When a bus stop marker is clicked, a new StopView is instantiated. This StopView instantiates a child RouteView for each stop_id it holds. The **RouteModel** attached to the RouteView view fetches from the **/departures** endpoint and then parses and attaches a rendered template to the infowindow above the marker.

While it's built to be responsive, there are still a few visual bugs on the mobile-end and the heavy client-side processes make the application sluggish.

Improvements
====

There are five main improvements I want to make in the near-future.

> 1) Better automated testing.

> 2) Better display of bus stop data.

> 3) More travel agencies implemented.

> 4) Asynchronous requests to third-party API's.

> 5) Analytics.

**Automated Testing**

Due to not being familiar with the capabilities of Google Maps, my process on the frontend consisted mostly of hacking. Had I been more familiar of what I was capable of, I could have written better tests to accompany my code.

Admittedly, testing is where I need the most help. I have felt the pain of refactoring larger apps without proper test coverage, and I don't want to feel it again. I will be spending the next few days focused on writing unit tests for my Javascript frontend and improving my tests on my Flask backend. It's not something I'm proud of, but my process on this app was more of DDT than TDD :\

**Displaying Data**

It currently isn't as mobile-friendly as I would like it to be. I would like to experiment with using a tabbed modal popup to display bus stop information.

**More Agencies**

The backend is built to extend and incorporate new agencies with ease, so why not?

**Asynchronous Requests**

If the user is in a location with mulitple new bus stops, there is a consecutive series of long requests that need to take place before stop times can be registered. It should be beneficial to handle these asynchronously.

**Better Data**

I've made most of my design decisions on gut instinct. Ideally, I'd like to employ a simple A/B testing framework for the frontend to collect usage data. It would also be beneficial for me to build tools to measure processes on the backend to optimize accordingly.

Final Thoughts
=========

I had a lot of fun building this app and I've learned a ton. There is a lot left to implement, but I'm happy with the progress I've made so far!

If people can find use from the app, I would look into building native mobile applications to communicate with my API and offer a much slicker UI/UX.

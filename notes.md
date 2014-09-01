Uber Coding Challenge
====================

Initial Thoughts
---------------
1) Looks to be one of the more comprehensive and challening coding test I've had the pleasure of working on. I'm going with the **FULL-STACK** route.

2) Email service looks to be the easiest. I've done some Flask-Mailgun stuff before and the problem looks easy to solve. If the POST doesn't return a 200, handle the error appropriately, then try posting to a different email provider. The abstraction seems pretty straightforward.

3) However, since this is Uber, I want to use this opportunity to get more familiar with geolocation. I'll have to play around with the API's, but right now I'm the most interested in building out **Departure Times.**


First Steps
--------------
I need to plan accordingly to make the best usage of my time. 

1) The implementation of the RESTful backend should be relatively easy. I'll start by building the API as a simple proxy to the Public Transport API's. I don't think persistent storage is necessary at this point, but implementing a (redis) cache should help with load times and help prevent rate-limiting. Going to build it out with Flask.

2) I'll use redis for the cache. I'll be storing data from the request along with a time token. The time token will serve to a) determine if the data is stale, and b) if not past the "stale" threshhold, I can apply the time delta (time stored - time accessed) to the cached departure times.

3) Frontend will be built in with Backbone.js. Backbone is super light and I'm relatively familiar with it. I was looking forward to a project to learn Angular.js with, but I don't think this is the right time/place.

4) Geolocation is new to me, shouldn't be too hard. There is probably like a Google Maps API that does the heavy lifting and returns lat/long coordinates. I should be able to use lat/long coordinates to get stop_id's to pass into requests made by Backbone.

5) UI/UX can be pretty fun, but constantly changing things around can be a time-sink. I'll attempt a simple design and try to keep the tweaks to a minimum. I'll stick to using Bootstrap, nothing too fancy.

6) It doesn't look like I'm going to be graded on load balancing or devops stuff, so I'd rather deploy to Heroku > EC2 (and its FREE!) This shouldn't take much time either. Most of the time I'll spend on Heroku will be configuring services.

7) Automated testing is going to be the hardest. I haven't had as much exposure to GOOD testing practices as I would like. However, I've felt the pain of refactoring without proper test coverage, and I never want to feel it again. This will be the most time consuming, but potentially the most rewarding portion of the app. Flask has a specific unit-testing framework, and I'll probably use Jasmine/Mocha for the Javascript side.


1) Flask-RESTful
------------
I need to answer a few questions first.

**1) Which Public Transport API will I consume??**

**2) How do I plan on storing this data?**

**3) What data do I want available to my users? Why?**

1) Which Public Transport API will I consume?

I'll determine which API to consume by:
    - Functionality: Given a stop_id, I can determine when the next busses are coming with either 511 or NextBus. Nextbus is more detailed.
    - Rate Limiting: 2MB/20sec for NextBus, "can change at any time." 511 doesn't list rate limiting details?
    - Data Formatting: Both NextBus and 511 return XML. I have a preference for JSON but can make due with XML.

**Going to start with NextBus!**

2) How do I plan on storing this data?

To start out, I might just write the flask API to simply proxy to the public transport API. All I'd really need to do is pass along the GET requests and then format them into JSON to make it easier for the frontend. By writing the flask proxy it'll be easier to add caching functionality (or persistent data storage) later on.

3) What data do I want available to my users? Why?

Users want to know which busses will arrive (and when they will arrive) at nearby stations. I'll have to pass a **bus stop ID** as a parameter on my GET request and expect to receive a JSON object of the **next arrivals** and their **estimated arrival time** in the response.

API Endpoint: '/departures/<str:agency>/<str:stop_id>'

Possible Response Object: 
    { next_arrivals: 
        [  {'51': {'direction': 'North', 'estimated_arrival': 3} 
        ,  {'100': {'direction': 'North', 'estimated_arrival': 8}
        ,  {'14': {'direction': 'North', 'estimated_arrival': 12}
        ]
     }

2) Cache
--------
Implemented the cache as a @decorator with TTL as an optional argument. The cache improves load times and helps me not get rate-limited.

    - GET requests to NextBus are each around 1kb. 
    - I'd have to make 100 requests a second to get rate limited by NextBus (2mb/20s)
    - With my TTL at 60s, I can theoretically maintain info on a maximum of 6,000 stops at a time before getting rate limited (minimum = 2,000)
    - Most importantly, the cache keeps duplicate requests from hitting the NextBus API.

3) Backbone.js
----------


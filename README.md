# URL Shortener

This app serves an HTTP API to shorten URLs:

```sh
$ curl -H "Content-Type: application/json" -X POST http://localhost:5000/shorten_url -d {
	"url": "http://davtyan.org"
}

{
  "shortened_url": "http://localhost/i"
}

$ curl -H "Content-Type: application/json" -X GET http://localhost:5000/i

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to target URL: <a href="HTTP://davtyan.org/%3Cmartin%3E">HTTP://davtyan.org</a>.  If not click the link.
```

## Design

URL shorteners are used to make URLs short and easy to read.

1. URLs need to be hard to confuse when hand-written or read out loud, so let's only allow lowercase letters and numbers in URL codes (but not 0 as you can confuse it with O), hence 37 possible characters
2. URLs need to be short, so let's use the shortest codes possible. 37 ** x > 30 trillion pages out there, so x = 9 - maximum foreseeable code length. We should start with using shortest codes when possible
3. Avoid the situation where URL is reused too soon, as seeing a wrong URL would be perceived as bad service. Let's just delete unused URLs to free up space rather then reuse codes.

The web service is implemented with [Flask](flask.pocoo.org) web framework and uses [MongoDB](https://www.mongodb.com/) as a storage backend. URLs are inserted into MongoDB and assigned unique incremental integer IDs using a [Counters Collection](https://docs.mongodb.com/v3.0/tutorial/create-an-auto-incrementing-field/#use-counters-collection) pattern. IDs are mapped to short URL codes and back using a bijective mapping defined in `urlcodes.py`, so that long URLs can be quickly retrieved by short codes (`storage.py`).

## Installation

### Dependencies

To run the application you will need:

1. A MongoDB instance 
2. Python package dependencies, please refer to `requirements.txt`
3. For production: Web-server, e.g. [nginx](http://flask.pocoo.org/docs/0.12/deploying/uwsgi/#configuring-nginx)

### Running development server

Before running the server, adjust `settings.py` to match your Web-server and MongoDB configurations.

Set up MongoDB collections by running:

```
python storage.py setup
```

Then you can run the server in test mode:

```
python server.py
```

## Scaling

If the service is experiencing high traffic, you may want to horizontally scale MongoDB or/and free up space taken by unused URLs.

### Horizontal scaling

The application was designed with [hashed sharding](https://docs.mongodb.com/manual/core/hashed-sharding/#hashed-sharding) in mind. As the URL codes are sequential, hashed sharding will allow to distribute documents/requests evenly among shards. `_id` key in URL collection has a [hashed index](https://docs.mongodb.com/manual/core/index-hashed/#index-hashed-index) set up, so to shard it you just need to run in MongoDB console:

```javascript
sh.shardCollection( "<DB>.<URL_COLLECTION>", { "_id" : "hashed" } )
```

where `DB` and `URL_COLLECTION` are specified in `settings.py`.

### Freeing up space

To remove URLs that have not been visited for a while, run:

```sh
python storage.py cleanup
```

By default that will remove all URLs in the collection that have not been visited for more than 180 days (you can adjust this interval in `settings.py`). You also may want to schedule this command to be ran periodically, e.g. using Cron.

## Roadmap and remarks

If I had more time to work on this, I would prioritize the following:

1. Writing proper tests. I only tested in with `curl` on some trivial cases.
2. Saving MD5 hashes of URLs so if I have already shortened the given URL I return the old short code instead of creating a new one. I did not do so because searching the entire collection for a document containing a certain string (MD5 hash) would be costly without an index. Most likely this would be as easy as setting up another hashed index on `URL` field but I needed more research to confirm that.
3. Addressing security concerns: I would research a decent way to avoid XSS injections, etc. I would also add some redundancy into the short URL codes so that they could not be scanned sequentially. 

Regarding the scaling note, I omitted all steps I didn't have code for e.g. running multiple servers with a load balancer, etc.

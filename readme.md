omglivedata is a project I put together to prototype monitor dashboard using rethinkdb changefeed and websocket.
It requires python27, rethinkdb, gunicorn and gevent.

![Screenshot](/screen.png?raw=true "Screenshot")

### requirement
  * rethinkdb
  * python packages specified in requirements.txt

### start server:
make runserver

### start ingestion:
make ingest

### look at dashboard:
browse to localhost:8000

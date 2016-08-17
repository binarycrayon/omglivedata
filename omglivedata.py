"""
omglivedata main app
"""

import json, random, time, itertools, datetime
from flask import Flask, request, render_template
from flask_sockets import Sockets
from gevent import sleep
import rethinkdb as r

from config import Config
from db_manager import connect_db, get_table_for_today


app = Flask(__name__)
app.config.from_object('config.Config')
sockets = Sockets(app)


@sockets.route('/channel/stream/<metric>')
def stream_socket(ws, metric):
    """
    websocket /channel/stream/<metric>
    """
    with connect_db() as conn:
        table = get_table_for_today(metric)
        cursor = r.table(table).pluck(
            ['metric', 'timestamp', 'value']).changes().run(conn)
        while True:
            try:
                change = cursor.next(wait=False)
                ws.send(json.dumps(change))
            except r.errors.RqlTimeoutError:
                # keep the channel alive
                ws.send(json.dumps({
                    'x': time.time(),
                    'y': 0
                    }))
            except r.errors.ReqlOpFailedError as e:
                # table may not exist
                print e
                continue
            sleep(0.5)


@app.route('/')
def index():
    """
    render index
    """
    return render_template("index.html", metrics=json.dumps(Config.METRICS))


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

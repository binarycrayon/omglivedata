
import json, random, time, itertools, datetime
from flask import Flask, request, render_template
from flask_sockets import Sockets
from gevent import sleep
import rethinkdb as r


app = Flask(__name__)
app.config.from_object('config.Config')
sockets = Sockets(app)

convert = lambda val: {
                    'timestamp': val['timestamp'].to_epoch_time(),
                    'filer': val['filer'],
                    'size': val['size']
                    }

def get_db_table():
    """
    read-weekday-2, read-weekday-3
    """
    current_day = datetime.datetime.now()
    table_to_read = "weekday_{day}".format(
            day=current_day.weekday())
    return table_to_read



@sockets.route('/channel/stream')
def stream_socket(ws):
    with r.connect(HOST, db=DATABASE, port=28015) as conn:
        table = get_db_table()
        cursor = r.table(table).pluck(['dcue_timestamp', 'filer', 'size']).map(convert).changes().run(conn)
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
    # get a list of table
    with r.connect(HOST, db=DATABASE, port=28015) as conn:
        a = [i['filer'] for i in r.table(get_db_table('filer_reads')).pluck('filer').distinct().run(conn)]
    return render_template("index.html", filers=json.dumps(list(set(a+b))))


if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()

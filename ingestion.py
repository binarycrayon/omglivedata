"""
Ingest data to rethinkdb
"""

import os
from datetime import tzinfo, timedelta, datetime
from multiprocessing import Pool
from random import seed, randint
import time

import rethinkdb as r
import forgery_py

# RethinkDB server.
RDB_HOST = os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
RDB_DB = 'omglivedata'
RDB_TABLE = 'stream'


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


def random_datetime(past=False, min_delta=0, max_delta=20, tzinfo=UTC):
    """Random `datetime.date` object. Delta args are days."""
    delta = timedelta(seconds=forgery_py.date._delta(past, min_delta, max_delta))
    return datetime.now(tzinfo()) + delta


def generate_data():
    seed()
    return {
        'timestamp': ,
        'value'
    }


def ingest_data():
    """
    Ingest documents to 'ingest' table
    """
    with connect_to_db() as conn:
        while True:
            generate_data()
            r.table(RDB_TABLE).insert(p).run(conn)
            time.sleep(0.1)


if __name__ == "__main__":
    ingest_data()

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

connect_to_host = lambda: r.connect(host=RDB_HOST, port=RDB_PORT)
connect_to_db = lambda: r.connect(host=RDB_HOST, port=RDB_PORT, db=RDB_DB)


def setup_db():
    with connect_to_host() as conn:
        r.db_create(RDB_DB).run(conn)
    with connect_to_db() as conn:
        r.table_create(RDB_TABLE).run(conn)


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
        'name': forgery_py.name.full_name(),
        'address': forgery_py.address.street_address(),
        'gender': forgery_py.personal.gender(),
        'race': forgery_py.personal.race(),
        'birthday': random_datetime(past=True, max_delta=60*60*24*365*80),
        'height': randint(160, 185)
    }


def check_and_create_table():
    """
    Schedule creating table 2 hour before the next day
    """
    now = datetime.now()
    if now.hour == 22 and now.minute >= 00:
        check_and_create_next_table()

def ingest_data():
    """
    Ingest documents to 'ingest' table
    """
    with connect_to_db() as conn:
        while True:
            p = generate_person()
            r.table(RDB_TABLE).insert(p).run(conn)
            time.sleep(1)


if __name__ == "__main__":
    ingest_data()

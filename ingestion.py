"""
Ingest data to rethinkdb
"""

import os
from datetime import tzinfo, timedelta, datetime
from multiprocessing import Pool
from random import seed, randint, choice
import time
from config import Config
from db_manager import connect_db, get_table_for_today, setup_existing_table

import rethinkdb as r

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


def generate_data():
    seed()
    return {
        'timestamp': r.now(),
        'value': randint(10, 100) / 10
    }


def ingest_data():
    """
    Ingest documents to 'ingest' table
    """
    with connect_db() as conn:
        while True:
            try:
                data = generate_data()
                metric = choice(Config.METRICS)
                table = get_table_for_today(metric)
                r.table(table).insert(data).run(conn)
                time.sleep(0.01)
            except r.errors.ReqlOpFailedError:
                setup_existing_table()
            except KeyboardInterrupt:
                return


if __name__ == "__main__":
    ingest_data()

"""
omglivedata db manager
"""
import logging
from datetime import datetime, timedelta
import rethinkdb as r
from config import Config


# connect rethinkdb host
connect_db_host = lambda: r.connect(Config.DB_HOST, port=Config.DB_PORT)
# connect rethinkdb database
connect_db = lambda: r.connect(Config.DB_HOST, db=Config.DB_NAME,
    port=Config.DB_PORT)
# setup logger

logger_error = logging.getLogger('omglivedata_error')
logger_info = logging.getLogger('omglivedata_info')


def create_db():
    """
    create db
    """
    with connect_db_host() as conn:
        r.db_create(Config.DB_NAME).run(conn)


def get_table_for_tomorrow(metric_name_prefix):
    """
    get table for tomorrow in the format of 'metric_weekday_[0-6]'
    """
    current_day = datetime.now()
    tomorrow = current_day + timedelta(days=1)
    days_ago = tomorrow - timedelta(days=6)
    table_to_insert = "{metric_name_prefix}_weekday_{day}".format(
            metric_name_prefix=metric_name_prefix,
            day=tomorrow.weekday())
    table_to_delete = "{metric_name_prefix}_weekday_{day}".format(
            metric_name_prefix=metric_name_prefix,
            day=days_ago.weekday())
    return table_to_insert


def get_tables_for_tomorrow():
    return [get_table_for_tomorrow(prefix) for prefix in Config.METRICS]


def get_tables_for_today():
    return [get_table_for_today(prefix) for prefix in Config.METRICS]


def get_table_for_today(name_prefix):
    """
    read-weekday-2, read-weekday-3
    """
    current_day = datetime.now()
    table = "{name_prefix}_weekday_{day}".format(
            name_prefix=name_prefix,
            day=current_day.weekday())
    return table


def create_index(table, conn):
    r.table(table).index_create('timestamp').run(conn)


def schedule_check_and_create_table():
    """
    Schedule creating table 2 hour before the next day
    """
    now = datetime.now()
    if now.hour == 22 and now.minute >= 00:
        check_and_create_next_table()


def setup_existing_table():
    try:
        create_db()
        logger_info.info('creating table {0}'.format(table))
    except r.errors.ReqlOpFailedError as e:
        logger_error.exception(e)
        logger_error.error('db already exists.')
    with connect_db() as conn:
        try:
            r.db_create(Config.DB_NAME).run(conn)
        except r.errors.ReqlOpFailedError as e:
            logger_error.error('db {0} already exists.'.format(Config.DB_NAME))
        for table in [get_table_for_today(i) for i in Config.METRICS]:
            try:
                logger_info.info('creating table {0}'.format(table))
                r.db(Config.DB_NAME).table_create(table, durability='soft',
                    shards=Config.DB_SHARDS).run(conn)
                create_index(table, conn)
            except r.errors.ReqlOpFailedError:
                print 'table {0} exists'.format(table)


def check_and_create_table_for_today():
    with connect_db() as conn:
        for table_to_add in get_insert_tables():
            try:
                r.table_create(table_to_add, durability='soft',
                    shards=SHARDS).run(conn)
            except r.errors.ReqlOpFailedError as e:
                logger_info.info(e)
                logger_info.info('dropping and re-adding {0}'.format(
                    table_to_add))
                r.table_drop(table_to_add).run(conn)
                r.table_create(table_to_add, durability='soft',
                    shards=SHARDS).run(conn)
            except Exception as e1:
                logger_error.error('exception at check and insert table')
                logger_error.exception(e1)
            finally:
                create_index(table_to_add, conn)


def check_and_create_table_for_tomorrow():
    """
    Prepare a table for tomorow, if the table already exist, it could be
    created a week ago. Drop it and re-create it.
    """
    with connect_db() as conn:
        for table in get_tables_for_tomorrow():
            try:
                r.table_create(table, durability='soft', shards=SHARDS).run(conn)
            except r.errors.ReqlOpFailedError as e:
                logger_info.info(e)
                logger_info.info('dropping and re-adding {0}'.format(table))
                r.table_drop(table).run(conn)
                r.table_create(table, durability='soft', shards=SHARDS).run(conn)
            except Exception as e1:
                logger_error.error('exception at check and insert next table')
                logger_error.exception(e1)
            finally:
                create_index(table_to_add, conn)

def schedule_check_and_create_table():
    """
    Schedule creating table 2 hour before the next day
    """
    now = datetime.now()
    if now.hour == 22 and now.minute >= 00:
        check_and_create_next_table()


if __name__ == '__main__':
    setup_existing_table()

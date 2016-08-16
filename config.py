"""
config module
"""

class Config(object):
    """
    Flask friendly configuration
    """
    DEBUG = True
    METRICS = ['io_reads', 'io_writes']
    DB_HOST = 'localhost'
    DB_NAME = 'omglivedata'
    DB_PORT = 28015
    DB_SHARDS = 1

# coding: utf-8

from tornado.process import cpu_count

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '******'

MYSQL_PUBLIC = 'test'

DEBUG = True
ECHOSQL = False

PUBLIC_STRING = 'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % (
    MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_PUBLIC)

THREAD_COUNT = cpu_count()

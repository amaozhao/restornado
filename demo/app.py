#!usr/bin/env python
# coding: utf-8

import os

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import db
from concurrent.futures import ThreadPoolExecutor
from tornado.options import define, options
from restornado.database import initialize_sessionmaker
from restornado.database.session import register_shutdown_handler
from urls import urls
define("port", default=9999, help="run on the given port", type=int)

DEBUG = True


class Application(tornado.web.Application):

    def __init__(self):
        handlers = urls
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret="9lYKfMjhR3CkI/NEyZBSPPkdDe0AXUeehcpT3iIJbik=",
            debug=DEBUG,
            autoreload=DEBUG
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.executor = ThreadPoolExecutor(4)


def main():
    tornado.options.parse_command_line()
    engine = db.get_engine()
    initialize_sessionmaker(engine=engine)
    http_server = tornado.httpserver.HTTPServer(Application())
    register_shutdown_handler(http_server, engine)
    if not DEBUG:
        http_server.bind(options.port)
        http_server.start(4)
        tornado.ioloop.IOLoop.current().start()
    else:
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()

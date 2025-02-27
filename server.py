#coding=utf-8
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.escape
from tornado.options import define, options
from handlers.urls import handlers
from config import settings

#定义一个默认的端口
define("port", default=8000, help="run port ", type=int)

if __name__ == "__main__":
    options.parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print('start server...')
    tornado.ioloop.IOLoop.instance().start()
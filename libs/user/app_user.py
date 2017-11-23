# -*- coding: utf-8 -*-
"""
Propose: User handlers API
Author: 'yac'
Date: 
"""

import time
import json

from tornado import websocket, gen
from tornado.web import asynchronous
from tornado.ioloop import IOLoop


from notification_api import queue
from .file_handler import FileHandler, FileShareHandler
from .user_handler import UserHandler, LoginHandler, LogoutHandler, RegisterHandler
from .calendar_handler import CalendarHandler
from .friend_handler import FriendHandler
from .base_handler import BaseHandler


# todo make reconnect in backend and frontend if error
class WebSocketHandler(websocket.WebSocketHandler, BaseHandler):

    @asynchronous
    @gen.engine
    def on_message(self, message):
        client = json.loads(message)

        while True:
            for _ in xrange(queue.qsize()):
                queue_obj = queue.get()
                if int(queue_obj['user_id']) == int(client['id']):
                    print 'send', queue_obj
                    try:
                        self.write_message(json.dumps(queue_obj))
                    except websocket.WebSocketClosedError:
                        print 'Get errorr'
                        queue.put(queue_obj)
                else:
                    queue.put(queue_obj)

            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 2)

   # def on_close(self):
   #     if self.id in clients:
   #         del clients[self.id]

    def check_origin(self, origin):
        return True

    #def open(self):
    #    self.write_message("ws-echo: 418 I'm a teapot (as per RFC 2324)")


handlers = [(r"/", LoginHandler),
            (r"/ws", WebSocketHandler),
            (r"/logout", LogoutHandler),
            (r"/register", RegisterHandler),
            (r"/user/(?P<login>[^\/]+)/calendar/?(?P<event_id>[0-9]+)?", CalendarHandler),
            (r"/user/(?P<login>[^\/]+)/file/?(?P<file_id>[0-9]+)?", FileHandler),
            (r"/user/(?P<login>[^\/]+)/file/?(?P<file_id>[0-9]+)/share", FileShareHandler),
            (r"/user/(?P<login>[^\/]+)/friend/?(?P<friend_id>[0-9]+)?", FriendHandler),
            (r"/user/(?P<login>[^\/]+)/?(?P<extend>[^\/]+)?", UserHandler)]

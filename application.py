import os
import tornado.web
import tornado.websocket
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.web import asynchronous
import json
import time

from libs.user.app_user import user_handlers, BaseHandler
from libs.oauth_api import oauth_handlers
from libs.user.notification_api import queue

# Constants.
APP_NAME = u"Tornado On OpenShift"
APP_VERSION = u"1.0"
COOKIE_SECRET = u"Rock_You_Like_A_Hurricane"
# TORNADO_PNG_URI = u"http://www.tornadoweb.org/en/stable/_images/tornado.png"


# The tornado application.
class Application(tornado.web.Application):
    def __init__(self):
        repodir = get_repo_dir()
        settings = dict()

        settings["title"] = APP_NAME
        settings["login_url"] = '/'
        settings["cookie_secret"] = u"Rock_You_Like_A_Hurricane"
        settings["static_path"] = os.path.join(repodir, "static")
        settings["template_path"] = os.path.join(repodir, "template")
        settings["xsrf_cookies"] = False
#        settings["debug"] = False

        handlers = [(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': settings["static_path"]}),
                    (r"/ws", WebSocketEchoHandler)]

        handlers.extend(user_handlers)
        handlers.extend(oauth_handlers)

        tornado.web.Application.__init__(self, handlers, **settings)


# Get the repo directory.
def get_repo_dir():
    repodir = os.getenv("OPENSHIFT_REPO_DIR")
    return repodir if repodir else os.path.abspath('./')


# Check if hot deployment is enabled.
def hot_deploy_marker():
    repodir = get_repo_dir()
    hdmarker = os.path.join(repodir, ".openshift", "markers", "hot_deploy")
    return os.path.exists(hdmarker)
 

# WebSocket echo handler.
class WebSocketEchoHandler(tornado.websocket.WebSocketHandler, BaseHandler):

    @asynchronous
    @gen.engine
    def on_message(self, message):
        client = json.loads(message)

        while True:
            for _ in xrange(queue.qsize()):
                queue_obj = queue.get()
                if int(queue_obj['user_id']) == int(client['id']):
                    self.write_message(json.dumps(queue_obj['msg']))
                else:
                    queue.put(queue_obj)

            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 2)

#    def on_close(self):
#        if self.id in clients:
#            del clients[self.id]

    def check_origin(self, origin):
        return True

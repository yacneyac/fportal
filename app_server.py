# -*- coding: utf-8 -*-
import os
from tornado import web

from libs.user.app_user import handlers as user_handlers
from libs.oauth_api import oauth_handlers


class Application(web.Application):
    """ Tornado application """

    def __init__(self):
        repodir = get_repo_dir()
        settings = dict()

        settings["login_url"] = '/'
        settings["cookie_secret"] = u"Rock_You_Like_A_Hurricane"
        settings["static_path"] = os.path.join(repodir, "static")
        settings["template_path"] = os.path.join(repodir, "templates")
        settings["xsrf_cookies"] = False

        handlers = [(r"/static/(.*)", web.StaticFileHandler, {'path': settings["static_path"]})]

        handlers.extend(user_handlers)
        handlers.extend(oauth_handlers)

        web.Application.__init__(self, handlers, **settings)


# Get the repo directory.
def get_repo_dir():
    repodir = os.getenv("OPENSHIFT_REPO_DIR")
    return repodir if repodir else os.path.abspath('./')


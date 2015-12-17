#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# pylint: disable=C0103,W0212,W0613
"""
Propose: User handlers API
Author: 'yac'
Date: 
"""

import json
import tornado.web
from tornado.web import HTTPError, RequestHandler
from tornado.escape import json_encode

from user_api import User, UserAPI
from calendar_api import CalendarAPI
from file_api import FileAPI, ShareFile
from friend_api import FriendAPI
from libs.logger import ac as log


def json_out(func):
    def wrapper(self, **kwargs):
        return self.write(json_encode(func(self, **kwargs)))
    return wrapper


class BaseHandler(RequestHandler):
    """ Base handler api """

    def initialize(self):
        """ Set arguments from GET and POST """
        self.args = {}

        # get json
        if not self.request.arguments and not self.request.files and self.request.body:
            self.args = json.loads(self.request.body)

        for value in self.request.arguments:
            arg = self.get_arguments(value)
            self.args[value] = arg[0] if len(arg) == 1 else arg

    def get_current_user(self):
        """ Search current user by cookie """
        if not self.get_secure_cookie('login') and not self.get_secure_cookie('user_id'):
            return None
        return User(self.get_secure_cookie('login'), self.get_secure_cookie('user_id'))

    # todo catch http error
    def write_error(self, status_code, **kwargs):
        if status_code in [500, 503, 404, 400]:
            log.exception('Code: %s', status_code)
            self.set_header('Content-Type', 'application/json')

            self.write(json_encode({'success': False, 'errorMessage': 'server_error'}))
        else:
            self.write('BOOM!')


class UserHandler(BaseHandler):
    """ User handler api """

    @tornado.web.authenticated
    def get(self, **kwargs):

        if kwargs['login'] == self.current_user.login:
            user_api = UserAPI(self.current_user)
            set_permission = False
        else:  # view another user
            user_api = UserAPI(User(login=kwargs['login']))
            set_permission = True

        params = {'menu': [],
                  'info': {
                    'first_name': user_api.user_db.first_name,
                    'middle_name': user_api.user_db.middle_name,
                    'second_name': user_api.user_db.second_name,
                    'birthday': user_api.user_db.birthday,
                    'email': user_api.user_db.email
                  },
                  'permission': {'v_file': user_api.user_db.v_file,
                                 'v_calendar': user_api.user_db.v_calendar,
                                 'v_friend': user_api.user_db.v_friend},
                  'id': user_api.user_db.id,
                  'avatar': user_api.user_db.avatar}

        # todo update set permission process
        if set_permission:
            if user_api.user_db.v_file:
                params['menu'].append('Documents')
            if user_api.user_db.v_calendar:
                params['menu'].append('Calendar')
            if user_api.user_db.v_friend:
                params['menu'].append('Friends')
        else:
            params['menu'].extend(['Documents', 'Calendar', 'Friends'])

        if not kwargs['extend']:
            self.set_header('Content-Type', 'application/json')
            return self.write(json_encode({'success': True, 'result': params}))

        return self.render('user/%s' % kwargs['extend'], **params)

    @tornado.web.authenticated
    @json_out
    def post(self, **kwargs):
        self.set_header('Content-Type', 'application/json')

        if self.current_user.login != kwargs['login']:
            raise HTTPError(403, 'forbidden')

        user_api = UserAPI(self.current_user)
        user_api.params = self.args

        if kwargs['extend'] == 'avatar':
            return user_api.set_avatar(self.args['file'])

        return user_api.update()


class CalendarHandler(BaseHandler):
    """ Calendar handler api """

    @tornado.web.authenticated
    @json_out
    def get(self, **kwargs):
        calendar = CalendarAPI(self.current_user)
        calendar.params = self.args
        return calendar.get_event()

    @tornado.web.authenticated
    @json_out
    def post(self, **kwargs):
        calendar = CalendarAPI(self.current_user)
        self.set_header('Content-Type', 'application/json')

        if kwargs['event_id']:
            if not self.request.body:
                return calendar.delete(kwargs['event_id'])

            return calendar.update(self.args)

        return calendar.insert(self.args)


class LoginHandler(BaseHandler):
    """ Login handler api """

    def get(self):
        self.render("index.html")

    @json_out
    def post(self):
        login = self.args.get('username')
        password = self.args.get('password')

        if login and password:

            user_api = UserAPI(User(login=login, password=password))
            user_api.env = self.request.headers

            if user_api.is_authorized():
                self.set_secure_cookie('login', login)
                self.set_secure_cookie('user_id', str(user_api.user_db.id))
                # TODO redirect by next in url
                # return self.redirect('/user/%s' % user_api.user_db.id)
                return {'success': True}

        return {'success': False, 'errorMessage': 'Invalid username/password'}


class LogoutHandler(BaseHandler):
    """ Logout handler api """

    @tornado.web.authenticated
    def get(self):
        self.clear_cookie('login')
        self.clear_cookie('user_id')
        self.redirect("/")


class RegisterHandler(BaseHandler):
    """ Registration handler api """

    @json_out
    def post(self):
        user = UserAPI(User())
        user.params = self.args
        return user.create()


class FileHandler(BaseHandler):
    """ File handler api """

    @tornado.web.authenticated
    def get(self, **kwargs):

        # file to zip
        if self.args['action'] == 'zf':

            file_api = FileAPI(self.current_user)
            file_api.params = self.args

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=files.zip')

            for chunk in file_api.to_zip():
                if chunk:
                    self.write(chunk)

            self.finish()
            return

        # download
        if self.args['action'] == 'df':

            file_api = FileAPI(self.current_user)
            file_api.set_file(kwargs['file_id'])

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + file_api.file_db.name)

            for chunk in file_api.read():
                if chunk:
                    self.write(chunk)

            self.finish()
            return

        # search
        if self.args['action'] == 'sf':
            f_api = FileAPI(self.current_user)
            f_api.params = self.args
            return self.write(json_encode(f_api.search()))

        if self.args['action'] == 'share':
            f_api = ShareFile(self.current_user)
            self.set_header('Content-Type', 'application/json')
            return self.write(json_encode(f_api.share(kwargs['file_id'])))

    @tornado.web.authenticated
    @json_out
    def post(self, **kwargs):
        self.set_header('Content-Type', 'application/json')

        if kwargs['file_id'] and not self.request.body:
            file_api = FileAPI(self.current_user)
            file_api.set_file(kwargs['file_id'])
            return file_api.delete()

        f_obj = self.request.files.get('file')
        if f_obj:
            file_api = FileAPI(self.current_user, f_obj[0])
            return file_api.upload()

        file_api = ShareFile(self.current_user)
        file_api.params = self.args
        file_api.file_id = kwargs['file_id']
        return file_api.share_file()


class FriendHandler(BaseHandler):
    """ Friend handler api """

    @tornado.web.authenticated
    @json_out
    def get(self, **kwargs):
        friend_api = FriendAPI(self.current_user)
        return friend_api.get()

    @tornado.web.authenticated
    @json_out
    def post(self, **kwargs):
        friend_api = FriendAPI(self.current_user)
        friend_api.params = self.args
        return friend_api.set_group()


user_handlers = [(r"/", LoginHandler),
                 (r"/logout", LogoutHandler),
                 (r"/register", RegisterHandler),
                 (r"/user/(?P<login>[^\/]+)/calendar/?(?P<event_id>[0-9]+)?", CalendarHandler),
                 (r"/user/(?P<login>[^\/]+)/file/?(?P<file_id>[0-9]+)?", FileHandler),
                 (r"/user/(?P<login>[^\/]+)/friend/?(?P<friend_id>[0-9]+)?", FriendHandler),
                 (r"/user/(?P<login>[^\/]+)/?(?P<extend>[^\/]+)?", UserHandler)]

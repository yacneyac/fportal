from tornado.web import authenticated, HTTPError

from .base_handler import BaseHandler
from .user_api import UserAPI, User


class LoginHandler(BaseHandler):
    """ Login handler api """

    def get(self):
        self.render("index.html")

    def post(self):
        login = self.params.get('username')
        password = self.params.get('password')

        if login and password:

            user_api = UserAPI(User(login=login, password=password))
            user_api.env = self.request.headers

            if user_api.is_authorized():
                self.set_secure_cookie('login', login)
                self.set_secure_cookie('user_id', str(user_api.user_db.id))
                # TODO redirect by next in url
                # return self.redirect('/user/%s' % user_api.user_db.id)
                self.finish({'success': True})

        self.finish({'success': False, 'errorMessage': 'Invalid username/password'})


class LogoutHandler(BaseHandler):
    """ Logout handler api """

    @authenticated
    def get(self):
        self.clear_cookie('login')
        self.clear_cookie('user_id')
        self.redirect("/")


class RegisterHandler(BaseHandler):
    """ Registration handler api """

    def post(self):
        user = UserAPI(User())
        user.params = self.params
        # self.request.set_code = 201
        self.finish(user.create())


class UserHandler(BaseHandler):
    """ User handler api """

    @authenticated
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
                    'birthday': int(user_api.user_db.birthday) if user_api.user_db.birthday else '',
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
            self.finish({'success': True, 'result': params})

        self.render('user/%s' % kwargs['extend'], **params)

    @authenticated
    def post(self, **kwargs):
        if self.current_user.login != kwargs['login']:
            raise HTTPError(403, 'forbidden')

        user_api = UserAPI(self.current_user)
        user_api.params = self.params

        if kwargs['extend'] == 'avatar':
            self.finish(user_api.set_avatar(self.params['file']))

        self.finish(user_api.update())

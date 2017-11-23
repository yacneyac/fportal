import json

from tornado.web import RequestHandler
from tornado.escape import json_encode

from libs.logger import ac as log
from .user_api import User


# def json_response(func):
#     def wrapper(self, **kwargs):
#         return self.write(json_encode(func(self, **kwargs)))
#     return wrapper


class BaseHandler(RequestHandler):
    """ Base handler api """

    def initialize(self):
        """ Set arguments from GET and POST """
        self.params = {}

        if self.request.method in ('POST', 'PUT') and not self.request.files:
            self.params = json.loads(self.request.body)
            # self.request.body_arguments

        #
        for value in self.request.arguments:
            arg = self.get_arguments(value)
            self.params[value] = arg[0] if len(arg) == 1 else arg

    def get_current_user(self):
        """ Search current user by cookie """
        user_login = self.get_secure_cookie('login')
        user_id = self.get_secure_cookie('user_id')
        if user_login and user_id:
            return User(user_login, user_id)
        return None


    # todo catch http error
    def write_error(self, status_code, **kwargs):
        if status_code in [500, 503, 404, 400]:
            log.exception('Code: %s', status_code)
            self.set_header('Content-Type', 'application/json')

            self.write(json_encode({'success': False, 'errorMessage': 'server_error'}))
        else:
            self.write('BOOM!')

    # def response(self, data):
    #     return self.write(json_encode(data))


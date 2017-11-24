# -*- coding: utf-8 -*-
"""
Propose: Describe user API
Author: 'yac'
Date: 
"""

import re
import os
import hashlib
from datetime import datetime
from ipwhois import IPWhois

from libs.models import UserDB, Stat
from client_parser import simple_detect
from libs.db.db_api import DataBaseAPI
from libs.conf import UPLOAD_AVATAR
from libs.logger import ac as log

EMAIL_REGEX = r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


# TODO open profile from another user

class User(object):
    """ Base User """
    def __init__(self, login=None, user_id=None, password=None):
        self.login = login
        self.id = user_id
        self.password = password


class UserAPI(object):
    """ Implemented User api """

    def __init__(self, user):

        self.login = user.login
        self.user_id = user.id
        self.password = user.password

        self.params = {}
        self.env = {}
        self.err_msg = ''

        self.db = DataBaseAPI(UserDB)
        self.user_db = self._set_user_db()

    def _set_user_db(self):
        """ Get UserDB object """
        # use user's login on first login to app
        if self.login:
            return self.db.get_obj('login="%s"' % self.login)

        return self.db.get_by_id(self.user_id)

    def is_authorized(self):
        """ Check auth user """
        if self.user_db and self._is_correct_pass() and self.user_db.active:
            self.set_statistic()
            # todo implement online block on WEBSOCKET
            self.set_online()
            return True

        return False

    def is_error(self):
        """ Check error """
        for param in UserDB.REQ_FIELDS:
            if not self.params.get(param, ''):
                self.err_msg = 'Empty %s' % param
                return True

        if len(self.params['login']) <= 2:
            self.err_msg = 'Username must be at list 3'
            return True

        if self.db.get_obj('login="%s"' % self.params['login']):
            self.err_msg = 'Login is present'
            return True

        if self.params.get('email'):
            if self.db.get_obj('email="%s"' % self.params['email']):
                self.err_msg = 'Email is present'
                return True

            if not re.match(EMAIL_REGEX, self.params['email']):
                self.err_msg = 'Incorrect email'
                return True

        if self.params['password'] != self.params['confpassword']:
            self.err_msg = 'Different value in password field'
            return True

        return False

    def set_avatar(self, file_obj):
        """ Set avatar for user """
        log.debug('Try to set avatar for user ID: %s', self.user_id)

        upload_dir = os.path.join(UPLOAD_AVATAR, str(self.user_id))
        if not os.path.exists(upload_dir):
            log.debug('--> Create avatar\'s dir.')
            os.makedirs(upload_dir)

        current_ava = os.path.join(upload_dir, self.user_db.avatar or '')
        if os.path.isfile(current_ava):
            log.debug('--> Delete current avatar.')
            os.remove(current_ava)

        file_path = os.path.join(upload_dir, file_obj['name'])

        with open(file_path, "wb") as f:
            f.write(file_obj['body'].decode('base64'))

        self.user_db.avatar = file_obj['name']

        self.db.commit()
        log.debug('--> Avatar has been set.')

        return {'success': True}

    def set_online(self):
        self.user_db.online = 1
        self.db.commit()

    def set_statistic(self):
        """ Save user's statistic """
        sw_ver, app_ver = simple_detect(self.env.get('User-Agent'))

        user_ip = self.env.get('HTTP_X_CLIENT_IP') or 'localhost'

        location = ''
        if user_ip != 'localhost':
            result = IPWhois(user_ip).lookup()

            location = result['nets'][0]['country']
            if result['nets'][0]['city']:
                location = '/'.join((location, result['nets'][0]['city']))

        stat = Stat(login=self.login,
                    user_ip=user_ip,
                    user_agent=app_ver,
                    user_os=sw_ver,
                    location=location,
                    date_login=datetime.now().strftime(DATE_FORMAT))

        self.db.create(stat)
        self.db.commit()
        log.debug('Set statistic for user: %s', self.user_id)

        return True

############### ADMIN
#    def search(self):
#        """ Search users """
#        db_api = DataBaseAPI(UserDB)

#        self.db.sql = SQL.format(table=UserDB.__tablename__)
#        self.db.params = self.params
#        self.db.search_fields = ['login', 'email', 'fio']
#        self.db.default_sort = 'login'
#
#        return self.db.search()

#    def delete(self):
#        """ Delete user """
#        self.db.session.query(UserDB).filter(UserDB.id == self.params['user_id']).delete()
#        self.db.session.commit()
#        self.db.session.close()
#        #        log.debug('UserDB <%s> has been deleted.', self.params['user_id'])
#
#        return {'success': True}


#    def get_statistic(self):
#        """ Search statistic by user """
#        db_api = DataBaseAPI(Stat)

#        self.db.sql = SQL.format(table=Stat.__tablename__)
#        self.db.params = self.params
#        self.db.search_fields = ['login', 'user_ip']
#        self.db.default_sort = 'login'
#
#        return self.db.search()
########################################

    def update_password(self, check=True):
        """ Update password """
        if check and not self._is_correct_pass():
            return {'success': False, 'errorMessage': 'incorrect current pass'}

        self.user_db.password = self._to_hash(self.params['newpassword'])
        self.db.commit()

        log.debug('New password has been set.')
        return {'success': True}

    def update(self):
        """ Update user's fields """
        for key, val in self.params.iteritems():
            if isinstance(val, basestring):
                self.params.update({key: val.encode('utf-8')})

        if 'password' in self.params.keys():
            if not self._is_correct_pass():
                return {'success': False, 'errorMessage': 'Incorrect current password!'}

            self.params['password'] = self._to_hash(self.params['newpassword'])
            del self.params['newpassword']
            del self.params['confpassword']

        self.db.update_field('login="%s"' % self.login, self.params)
        self.db.commit()
        log.debug('User ID: %s has been updated.', self.user_id)
        return {'success': True}

    def create(self):
        """ Create a new user """
        if self.is_error():
            log.error('Cannot create user. \n%s', self.err_msg)
            return {'success': False, 'errorMessage': self.err_msg}

        user = UserDB()
        user.login = self.params['login']
        user.email = self.params.get('email', '')
        user.password = self._to_hash(self.params['password'])
        user.first_name = self.params['first_name']

        self.db.create(user)
        self.db.commit()
        log.debug('User has been created.')

        return {'success': True}

    def _is_correct_pass(self):
        return self.user_db.password == self._to_hash(self.params.get('password') or self.password)

    @staticmethod
    def _to_hash(value):
        return hashlib.md5(value.encode('utf-8')).hexdigest()

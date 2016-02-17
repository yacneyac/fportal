# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""
from datetime import datetime

from libs.models import UserDB
from libs.logger import ac as log
from user_api import UserAPI
#from calendar_api import CalendarAPI, CalendarDB


# TODO API IS UNDER CONSTRUCTION


class SocialUser(UserAPI):
    """ Implemented api for user from social net """

    def save_to_db(self):
        """ Save information about social user to DB """
        # update
        if self.user_db:
            self.db.session.query(UserDB).filter(UserDB.login == self.params['login']).\
                    update({'access_token': self.params['access_token'],
#                            'social_net': self.params['social_net'] or 'social_net',
                            'profile_url': self.params.get('profile_url', None),
                            'fio': self.params.get('name', None),
                            'email': self.params.get('email', None)},
                           synchronize_session='fetch')
            self.db.commit()
            log.debug('Updated social user: %s', self.params['login'],)
        # create
        else:
            user = UserDB(self.params['login'],
                          self.params['email'],
                          fio = self.params['name'],
                          avatar = '',
                          access_token = self.params['access_token'],
                          social_net = self.params['social_net'],
                          profile_url = self.params['link']
                          )

            self.db.create(user)
            log.debug('Social user <%s> created', self.params['login'])
        return {'success': True}

#    def sync_calendar(self):
#        """ Sync calendar for user FB """
#        self.get_db_user()
#
#        access_token = '='.join(('access_token', self.user.access_token))
#        user_id = self.user.login
#
#        log.debug('Try to sync calendar for user: %s', user_id)
#
#        profile = json.load(urllib.urlopen("https://graph.facebook.com/%s/events?%s" % (user_id, access_token)))
#        # todo if profile expired by access_token generate another
#        if not 'data' in profile:
#            return
#
#        calendar = CalendarAPI(self.user.id)
#
#        event_db_list = CalendarDB.query.filter(CalendarDB.user_id==self.user.id,
#                                                CalendarDB.event_source.like('fb')).all()
#
#        for event in profile['data']:
#            event['ext_id'] = event.pop('id')  # rename fb event id to ext_id
#
#            event['start_time'] = self.convert_date(event['start_time'])
#            if 'end_time' in event:
#                event['end_time'] = self.convert_date(event['end_time'])
#
#            for index, event_db in enumerate(event_db_list):  # search fb id in DB for update
#                if event['ext_id'] == event_db.ext_id:
#
#                    event['id'] = event_db.id  # add id from db for update
#                    del event_db_list[index]  # event will be update - del from db_list
#
#                    calendar.update(event)
#                    break
#
#            # INSERT
#            event['url'] = 'https://www.facebook.com/events/%s' % event['ext_id']
#            event['source'] = 'fb'
#
#            calendar.insert(event)
#
#        for event_db in event_db_list:
#            calendar.delete(event_db.id)

    def convert_date(self, date):
        if 'T' in date:
            dd = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+0300')
            return dd.strftime('%d-%m-%Y %H:%M:%S')
        else:
            dd = datetime.strptime(date, '%Y-%m-%d')
            return dd.strftime('%d-%m-%Y')

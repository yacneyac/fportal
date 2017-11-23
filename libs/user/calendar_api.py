# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

from datetime import datetime
from tornado.web import HTTPError, Finish
from libs.models import CalendarDB
from libs.logger import ac as log
from libs.db.db_api import DataBaseAPI


# class Success(object):
#     answer = None
#
#     def __call__(self, **kwargs):
#         self.answer = {'success': True}.update(kwargs)
#
#
# success = Success().answer

def fail(**params):
    err = {'success': False}
    err.update(params)
    return err


def success(**params):
    ok = {'success': True}
    ok.update(params)
    return ok


class CalendarAPI(object):
    """ Calendar API """

    def __init__(self, user):
        self.user_id = user.id
        self.db = DataBaseAPI(CalendarDB)

    def get_event(self):
        """Get events"""
        events_db = self.db.get_all('user_id = %s' % self.user_id)
        return success(result=[event.to_dict() for event in events_db])

    def insert(self, event):
        """ Add a new event """
        db_event = CalendarDB()

        db_event.user_id = self.user_id
        db_event.title = event['title'].encode('utf-8')
        db_event.event_class = event['type']
        db_event.start_at = event['startsAt']
        db_event.end_at = event.get('endsAt')
        db_event.desc = event.get('desc')
        db_event.ext_id = event.get('ext_id')
        db_event.url = event.get('url')
        db_event.event_source = event.get('source')
        db_event.recurs_on = event.get('recursOn')

        self.db.create(db_event, commit=False)
        self.db.flush()
        self.db.update(db_event)
        self.db.commit()

        log.debug('Event has been set for user ID: %s', self.user_id)
        return success(id=db_event.id) #{'success': True, 'id': db_event.id}

    def update(self, event):
        """ If event exists in DB, update it """
        db_event = self.db.get_by_id_or_404(event['id'])

        db_event.title = event['title'].encode('utf-8')
        db_event.event_class = event['type']
        db_event.start_at = event['startsAt']
        db_event.end_at = event.get('endsAt')
        db_event.desc = event.get('desc')
        db_event.recurs_on = event.get('recursOn')

        self.db.update(db_event)

        log.debug('Event <%s> has been updated.', event['id'])
        return success()

    def delete(self, event_id):
        """ Delete event """
        # todo: get event first
        self.db.delete_by_id(event_id)
        log.debug('Event <%s> has been deleted.', event_id)
        return success()

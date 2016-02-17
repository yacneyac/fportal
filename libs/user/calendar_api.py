# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

from datetime import datetime

from libs.models import CalendarDB
from libs.logger import ac as log
from libs.db.db_api import DataBaseAPI


class CalendarAPI(object):
    """ Calendar API """

    def __init__(self, user):
        self.user_id = user.id
        self.params = {}

        self.db = DataBaseAPI(CalendarDB)

    def get_event(self):
        """Get events"""
        sql = "select * from calendar where user_id =%s" % self.user_id

        connection = self.db.engine.connect()
        result = connection.execute(sql)
        connection.close()

        events = [dict(zip(row.keys(), row)) for row in result]
        for event in events:
            for key, val in event.iteritems():
                if isinstance(val, datetime):
                    event[key] = str(val)

        return {'success': True, 'result': events}

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
        return {'success': True, 'id': db_event.id}

    def update(self, event):
        """ If event exists in DB, update it """
        db_event = self.db.get_obj('id="%s"' % event.get('id'))
        if db_event:
            db_event.title = event['title'].encode('utf-8')
            db_event.event_class = event['type']
            db_event.start_at = event['startsAt']
            db_event.end_at = event.get('endsAt')
            db_event.desc = event.get('desc')
            db_event.recurs_on = event.get('recursOn')

            self.db.update(db_event)

        log.debug('Event <%s> has been updated.', event['id'])
        return {'success': True}

    def delete(self, event_id):
        """ Delete event """
        self.db.delete_by_filter('id="%s"' % event_id)

        log.debug('Event <%s> has been deleted.', event_id)
        return {'success': True}

    # def __timestamp(self, date):
    #     if date:
    #         if ':' in date:
    #             dd = datetime.strptime(date,'%d-%m-%Y %H:%M:%S')
    #             dt = datetime(dd.year, dd.month, dd.day, dd.hour, dd.minute, dd.second)
    #             return time.mktime(dt.timetuple())*1000
    #
    #         dd = datetime.strptime(date,'%d-%m-%Y')
    #         dt = datetime(dd.year, dd.month, dd.day)
    #         return time.mktime(dt.timetuple())*1000

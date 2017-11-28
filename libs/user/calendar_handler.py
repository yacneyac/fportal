from tornado.web import authenticated

from .base_handler import BaseHandler
from .calendar_api import CalendarAPI


class CalendarHandler(BaseHandler):
    """ Calendar handler api """
    calendar = None

    def prepare(self):
        self.calendar = CalendarAPI(self.current_user)

    @authenticated
    def get(self, **kwargs):
        """Get all event for current user"""
        self.finish(self.calendar.get_event())

    @authenticated
    def post(self, **kwargs):
        """Update event"""
        self.finish(self.calendar.update(self.params))

    @authenticated
    def put(self, **kwargs):
        """Create event"""
        self.set_status(201)
        self.finish(self.calendar.insert(self.params))

    @authenticated
    def delete(self, **kwargs):
        """Delete event by id"""
        self.finish(self.calendar.delete(kwargs['event_id']))

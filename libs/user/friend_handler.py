from tornado.web import authenticated

from .base_handler import BaseHandler
from .friend_api import FriendAPI


class FriendHandler(BaseHandler):
    """ Friend handler api """

    def prepare(self):
        self.friend = FriendAPI(self.current_user, self.params)

    @authenticated
    def get(self, **kwargs):
        # if self.params.get('action') == 'l':
        #     return self.friend.get_likely_friends()
        if self.params.get('action') == 'r':
            self.finish(self.friend.get_request())

        self.finish(self.friend.get())

    @authenticated
    def post(self, **kwargs):
        if kwargs['friend_id']:
            if self.params.get('action') == 'add':
                print 'ADD', kwargs, self.params
                self.finish({'success': True})

            elif self.params.get('action') == 'del':
                print 'UNFRIEND', kwargs, self.params
                self.finish(self.friend.set_friend())

            elif self.params.get('action') == 'reject':
                print 'REJECT', kwargs, self.params
                self.finish({'success': True})

        self.finish(self.friend.set_group())

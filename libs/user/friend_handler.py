from tornado.web import authenticated

from .base_handler import BaseHandler
from .friend_api import FriendAPI


class FriendHandler(BaseHandler):
    """ Friend handler api """
    friend = None

    def prepare(self):
        self.friend = FriendAPI(self.current_user, self.params)

    @authenticated
    def get(self, **kwargs):
        if self.params.get('action') == 'new':
            self.finish(self.friend.get_new_friends())
        elif self.params.get('action') in ('my_req', 'req_me'):
            self.finish(self.friend.get_request())
        else:
            self.finish(self.friend.get_all())

    @authenticated
    def post(self, **kwargs):
        if kwargs['friend_id']:
            if self.params.get('action') == 'add':
                self.finish(self.friend.set_friendship(kwargs['friend_id']))
            elif self.params.get('action') == 'del':
                self.finish(self.friend.unset_friendship(kwargs['friend_id']))
            elif self.params.get('action') == 'reject':
                print 'REJECT', kwargs, self.params
                self.finish({'success': True})

        # todo: update api . need to use friend_id from kwargs
        else:
            self.finish(self.friend.set_group())

# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

from libs.models import NotificationDB
from libs.db.db_api import DataBaseAPI
from libs.logger import ac as log

from multiprocessing import Queue
queue = Queue()


class NotificationAPI(object):
    """ Implemented notification api """

    SHARE_DOCUMENT = 'share_doc'
    NEW_MESSAGE = 'new_msg'
    NEW_FRIEND = 'new_friend'
    REQUEST = 'req_friend'

    @staticmethod
    def send(sender, receiver, msg_type, message):
        """ Add notification """
        db_api = DataBaseAPI(NotificationDB).session

        note = NotificationDB()

        note.sender = sender
        note.receiver = receiver
        note.msg_type = msg_type
        note.message = message
        note.read = 0

        db_api.add(note)
        db_api.commit()
        db_api.close()

        queue.put({'user_id': receiver, 'msg': message, 'msg_type': msg_type})
        log.debug('Put notification to queue')

        return True

    @staticmethod
    def read(msg_id):
        """ Read message """
        db_api = DataBaseAPI(NotificationDB).session
        db_api.query(NotificationDB).filter(NotificationDB.id == msg_id).update({NotificationDB.read: 1})
        db_api.commit()
        db_api.close()

        return True

    @staticmethod
    def get(get_by=None):
        """ Get notification: all, by sender, by receiver
        get_by = ('sender/receiver', id)
        """
        if get_by:
            if len(get_by) != 2:
                return

            return NotificationDB.query.filter(NotificationDB.receiver == get_by[1]).all()
        else:
            return NotificationDB.query.all()

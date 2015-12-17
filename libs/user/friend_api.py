#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# pylint: disable=C0103,W0212,W0613
"""
Propose: 
Author: 'yac'
Date: 
"""

from libs.db.db_api import DataBaseAPI
from libs.logger import ac as log
from libs.models import FriendDB, FriendAssignedGroupDB


class FriendAPI(object):
    def __init__(self, current_user):
        self.user_id = current_user.id
        self.friend_db = DataBaseAPI(FriendDB)
        self.params = {}

    def get(self):
        sql = "SELECT f.friend_id id, concat(u.first_name, ' ', u.second_name) name, u.avatar "\
                              "FROM friend f inner join user u on u.id = f.friend_id "\
                              "where f.user_id=%s" % self.user_id
        sql_assigned_group = "select fg.id group_id, fag.friend_id from friend_assigned_group fag "\
                             "inner join friend_group fg on fg.id = fag.group_id where fag.user_id =%s" % self.user_id
        sql_group = "select * from friend_group"

        connection = self.friend_db.engine.connect()
        friends_db = connection.execute(sql)
        assigned_group_db = connection.execute(sql_assigned_group)
        group_db = connection.execute(sql_group)
        connection.close()

        friends = [dict(zip(friends_db.keys(), row)) for row in friends_db]
        assigned_groups = [dict(zip(assigned_group_db.keys(), row)) for row in assigned_group_db]
        groups = [dict(zip(group_db.keys(), row)) for row in group_db]

        for friend in friends:
            friend['groups'] = []

            for group in groups:
                c_group = group.copy()
                c_group['assigned'] = False

                for assigned_group in assigned_groups:
                    if c_group['id'] == assigned_group['group_id'] and assigned_group['friend_id'] == friend['id']:
                        c_group['assigned'] = True
                        break

                friend['groups'].append(c_group)

        return {'success': True, 'friends': friends}

    def set_group(self):
        """ Setting group for user """
        log.debug('Set group for friend')

        group_db_api = DataBaseAPI(FriendAssignedGroupDB)
        friend_to_group = FriendAssignedGroupDB()

        if self.params['assigned']:
            friend_to_group.user_id = self.user_id
            friend_to_group.friend_id = self.params['friend_id']
            friend_to_group.group_id = self.params['id']

            group_db_api.create(friend_to_group)
        else:
            assigned_group = group_db_api.get_obj('group_id=%s and friend_id=%s and user_id=%s' %
                                                  (self.params['id'], self.params['friend_id'], self.user_id))
            group_db_api.delete(assigned_group)

        group_db_api.commit()
        return {'success': True}

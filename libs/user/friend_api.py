# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

from libs.db.db_api import DataBaseAPI
from libs.logger import ac as log
from libs.models import FriendDB, DictFriendStatusDB, FriendAssignedGroupDB


class FriendAPI(object):

    def __init__(self, current_user, params=None):
        self.user_id = current_user.id
        self.db = DataBaseAPI(FriendDB)
        self.params = params

        self.status = DictFriendStatusDB

    def get_likely_friends(self):
        sql = "select u.id, concat(u.first_name, ' ', u.second_name) name, u.avatar from user u "\
              "where u.id not in " \
              "(select friend_id from friend where user_id={0}) and u.id!={0}".format(self.user_id)
        friends_db = self.db.execute(sql)
        return {'success': True, 'new_friends': [dict(zip(friends_db.keys(), row)) for row in friends_db]}

    def get_request(self):
        """Get people who want to friend with user"""

        # if self.params['action'] == 'my_req':
        #     sql = "select f.id relation_id, "\
        #           "f.friend_id id, concat(u.first_name, ' ', u.second_name) name, u.avatar "\
        #           "from friend f inner join user u on u.id = f.friend_id "\
        #               "where f.user_id=%s and f.status=2" % self.user_id

        # else:
        sql = "select f.id relation_id, f.user_id id, "\
              "concat(u.first_name, ' ', u.second_name) name, u.avatar, u.online "\
              "from friend f inner join user u on u.id = f.user_id "\
              "where f.friend_id=%s and f.status=2" % self.user_id

        friends_db = self.db.execute(sql)
        return {'success': True, 'r_friends': [dict(zip(friends_db.keys(), row)) for row in friends_db]}

    def get(self):
        # sql = "SELECT f.friend_id id, f.id relation_id, concat(u.first_name, ' ', u.second_name) name, " \
        #           "u.avatar, u.online, (select id from friend where status=1 and user_id=u.id) initial_id "\
        #           "FROM friend f inner join user u on u.id = f.friend_id "\
        #           "where f.user_id=%s and f.status=1" % self.user_id
        sql = "SELECT f.friend_id id, f.id relation_id, concat(u.first_name, ' ', u.second_name) name, " \
                  "u.avatar, u.online "\
                  "FROM friend f inner join user u on u.id = f.friend_id "\
                  "where f.user_id=%s and f.status=1" % self.user_id
        sql_assigned_group = "select fg.id group_id, fag.friend_id from friend_assigned_group fag "\
                             "inner join friend_group fg on fg.id = fag.group_id where fag.user_id =%s" % self.user_id
        sql_group = "select * from friend_group"

        friends_db, assigned_group_db, group_db = self.db.execute((sql, sql_assigned_group, sql_group))

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

        return {'success': True, 'friends': friends, 'groups': [grp['name'] for grp in groups]}

    def set_group(self):
        """ Setting group for user """
        log.debug('Set group for friend')

        group_db_api = DataBaseAPI(FriendAssignedGroupDB)

        if self.params['assigned']:
            friend_to_group = FriendAssignedGroupDB()
            friend_to_group.user_id = self.user_id
            friend_to_group.friend_id = self.params['friend_id']
            friend_to_group.group_id = self.params['id']

            group_db_api.create(friend_to_group)
            group_db_api.commit()

            return {'success': True}

        flt = 'group_id=%s and friend_id=%s and user_id=%s' % \
              (self.params['id'], self.params['friend_id'], self.user_id)
        group_db_api.delete_by_filter(flt)
        group_db_api.commit()

        return {'success': True}

    def set_friendship(self, friend_id=None):
        """ Make friendship with other user  """
        # for every request for friendship a new relation is created in FriendDB
        new_friendship = FriendDB()
        new_friendship.user_id = int(self.user_id)
        new_friendship.friend_id = int(friend_id)
        new_friendship.status = self.status.PENDING

        # get answer from a new friend
        if 'relation_id' in self.params:
            new_friendship.status = self.status.FRIEND  # set friendship for friend

            # set friendship for current user
            friendship = self.db.get_by_id_or_404(self.params['relation_id'])
            friendship.status = self.status.FRIEND

        # create a new friendship and update old
        self.db.create(new_friendship)
        self.db.commit()

        return {'success': True, 'id': new_friendship.id}

    def unset_friendship(self, friend_id):
        # todo: make cancel ?
        flt = 'user_id=%s and friend_id=%s' % (int(friend_id), self.user_id)

        self.db.delete_by_filter(flt)
        self.db.delete_by_id(self.params['relation_id'])
        self.db.commit()

        return {'success': True}
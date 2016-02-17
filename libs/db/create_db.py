#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""
import hashlib

from libs.models import *
from libs.conf import DB_USER, DB_PASS, DB_HOST, DB_NAME
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


ADMIN_LOGIN = 'admin'
ADMIN_PASS = 'admin'


def insert(engine, tname, value, field='value'):
    conn = engine.connect()
    conn.execute('INSERT INTO %s (%s) VALUES ("%s")' % (tname, field, value))
    conn.close()

if __name__ == '__main__':
    uri = 'mysql://%s:%s@%s/%s' % (DB_USER, DB_PASS, DB_HOST, DB_NAME)

    engine = create_engine(uri)

    try:
        engine.connect()
    except OperationalError:
        engine = create_engine("mysql://%s:%s@%s" % (DB_USER, DB_PASS, DB_HOST))
        conn = engine.connect()
        conn.execute("create database %s" % DB_NAME)
        conn.close()
        engine = create_engine(uri)

    for t in metadata.sorted_tables:
        print t.name

    metadata.drop_all(engine)
    print 'Tables has been deleted'
    metadata.create_all(engine)
    print 'Created table'

    conn = engine.connect()
    # add dict friend status
    for status in ('friend', 'pending', 'cancel'):
        t_name = DictFriendStatusDB.__tablename__
        insert(engine, t_name, status)

    print '--status friend dict has been created'


#    # add dict file permission
    for perm in ('modify', 'read'):
        t_name = DictPermissionDB.__tablename__
        insert(engine, t_name, perm)

    print '--file permission dict has been created'

#    # add dict group
    for group in ('Family', 'Close Friends'):
        t_name = FriendGroupDB.__tablename__
        insert(engine, t_name, group, 'name')

    print '--groups dict has been created'
#
#    # add dict notification
    for note in ('share_doc', 'new_msg', 'new_friend', 'req_friend'):
        t_name = DictNotificationDB.__tablename__
        insert(engine, t_name, note)
    print '--notification dict has been created'

    for user in ('user1', 'user2', 'user3', 'user4'):
        t_name = UserDB.__tablename__

        conn = engine.connect()
        conn.execute('INSERT INTO %s (login, email, password, active, first_name, second_name) VALUES'
                     ' ("%s", "%s", "%s", "%s", "%s", "%s")' %
                     (t_name, user, '', hashlib.md5(user).hexdigest(), 1, user, user))
        conn.close()

    # add admin user
    t_name = UserDB.__tablename__

    conn = engine.connect()
    conn.execute('INSERT INTO %s (login, email, password, active) VALUES ("%s", "%s", "%s", "%s")' %
                 (t_name, ADMIN_LOGIN, '', hashlib.md5(ADMIN_PASS).hexdigest(), 1))
    conn.close()
    print '--Admin user has been created'

    print '--test user created'

    for friend in ((2, 1, 1), (1, 2, 1), (2, 3, 1), (3, 2, 1)):
        t_name = FriendDB.__tablename__
        conn = engine.connect()
        conn.execute('INSERT INTO %s (user_id, friend_id, status) VALUES ("%s", "%s", "%s")' %
                     (t_name, friend[0], friend[1], friend[2]))
        conn.close()

    print '--friends has been created'



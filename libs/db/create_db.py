#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# pylint: disable=C0103,W0212,W0613
"""
Propose: 
Author: 'yac'
Date: 
"""
import hashlib

from libs.models import *
#from mainApp import app
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
#from sqlalchemy_utils import database_exists, create_database


ADMIN_LOGIN = 'admin'
ADMIN_PASS = 'admin'

def insert(engine, tname, value):
    conn = engine.connect()
    conn.execute('INSERT INTO %s (value) VALUES ("%s")' % (tname, value))
    conn.close()

if __name__ == '__main__':

#    engine = create_engine("mysql://root:yarcher@localhost/blik_db")
#    engine = create_engine("mysql://admin27Dg2P6:U74f21Q62Ub8@127.2.79.2:3306/fportal")
    engine = create_engine("mysql://root:yarcher@localhost/blik_db")
    try:
        engine.connect()
    except OperationalError:
        engine = create_engine("mysql://root:yarcher@localhost")
        conn = engine.connect()
        conn.execute("create database blik_db")
        conn.close()
        engine = create_engine("mysql://root:yarcher@localhost/blik_db")

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
#
#    # add dict notification
    for note in ('file', 'friend', 'message'):
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

    for friend in ((5,2,1), (5,3,1), (5,4,1)):
        t_name = FriendDB.__tablename__
        conn = engine.connect()
        conn.execute('INSERT INTO %s (user_id, friend_id, status) VALUES ("%s", "%s", "%s")' %
                     (t_name, friend[0], friend[1], friend[2]))
        conn.close()

    print '--friends has been created'


    # for group in ((5, 'Group1'), (5, 'Group2'), 'Group3'):
    #     t_name = FriendDB.__tablename__
    #     conn = engine.connect()
    #     conn.execute('INSERT INTO %s (user_id, name) VALUES ("%s", "%s")' %
    #                  (t_name, group[0], group[1]))
    #     conn.close()



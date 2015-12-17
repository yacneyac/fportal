#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: Describe models in DB
Author: 'yac'
Date: 
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class UserDB(Base):
    REQ_FIELDS = ('login', 'first_name', 'password')

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)

    login = Column(String(50), nullable=False, unique=True)
    email = Column(String(50))
    active = Column(Boolean(), nullable=False, server_default='1')
    registered_at = Column(String(50))
    first_name = Column(String(50))
    middle_name = Column(String(50))
    second_name = Column(String(50))
    birthday = Column(String(20))
    password = Column(String(45))
    avatar = Column(String(50))

    v_file = Column(Boolean(), nullable=False, server_default='0')
    v_calendar = Column(Boolean(), nullable=False, server_default='0')
    v_friend = Column(Boolean(), nullable=False, server_default='0')

    # todo make table oauth
    access_token = Column(String(800))
    social_net = Column(String(10))
    profile_url = Column(String(100))

    file_quota = Column(Integer(), server_default='5242880')  # 5Mb
    used_file_quota = Column(Integer(), server_default='0')  # bytes


class FileDB(Base):
    __tablename__ = 'file_store'

    id = Column(Integer(), primary_key=True)

    user_id = Column(Integer(), ForeignKey('user.id'))
    name = Column(String(200))
    size = Column(Integer())  # bytes
    type = Column(String(10))
    f_class = Column(String(10))
    date_load = Column(String(45))


class CalendarDB(Base):
    __tablename__ = 'calendar'

    id = Column(Integer(), primary_key=True)

    user_id = Column(Integer(), ForeignKey('user.id'))
    event_class = Column(String(20))
    event_source = Column(String(50))
    start_at = Column(String(10))
    end_at = Column(String(10))
    ext_id = Column(String(50))
    title = Column(String(100))
    desc = Column(String(500))
    url = Column(String(100))
    recurs_on = Column(String(10))


class FileShareDB(Base):
    __tablename__ = 'file_share'

    id = Column(Integer(), primary_key=True)

    file_id = Column(Integer(), ForeignKey('file_store.id'))
    user_own_id = Column(Integer(), ForeignKey('user.id'))
    user_assigned_id = Column(Integer(), ForeignKey('user.id'))
    permission = Column(Integer())  # 0, 1, 2
    date_shared = Column(String(50))


class DictPermissionDB(Base):
    __tablename__ = 'dict_file_permission'
    id = Column(Integer(), primary_key=True)
    value = Column(String(10))  # modify, read


class DictFriendStatusDB(Base):
    __tablename__ = 'dict_friend_status'

    id = Column(Integer(), primary_key=True)
    value = Column(String(10))  # pending, friend, cancel


class FriendDB(Base):
    __tablename__ = 'friend'

    id = Column(Integer(), primary_key=True)

    user_id = Column(Integer(), ForeignKey('user.id'))
    friend_id = Column(Integer(), ForeignKey('user.id'))
    status = Column(Integer(), ForeignKey('dict_friend_status.id'))


class FriendGroupDB(Base):
    __tablename__ = 'friend_group'

    id = Column(Integer(), primary_key=True)

    name = Column(String(20))


class FriendAssignedGroupDB(Base):
    __tablename__ = 'friend_assigned_group'

    id = Column(Integer(), primary_key=True)

    user_id = Column(Integer(), ForeignKey('user.id'))
    friend_id = Column(Integer(), ForeignKey('user.id'))
    group_id = Column(Integer(), ForeignKey('friend_group.id'))


class Stat(Base):
    __tablename__ = 'statistic'

    id = Column('id', Integer(), primary_key=True)

    login = Column('login', String(50), ForeignKey('user.login'))
    user_ip = Column('user_ip', String(50))
    location = Column('location', String(50))
    user_agent = Column('user_agent', String(80))
    user_os = Column('user_os', String(80))
    date_login = Column('date_login', String(80))


class NotificationDB(Base):
    __tablename__ = 'notification'

    id = Column('id', Integer(), primary_key=True)

    sender = Column(Integer(), ForeignKey('user.id'))
    receiver = Column(Integer(), ForeignKey('user.id'))
    msg_type = Column(Integer(), ForeignKey('dict_notification.id'))
    message = Column(String(500))
    read = Column(Integer())  # 1,0


class DictNotificationDB(Base):
    __tablename__ = 'dict_notification'

    id = Column('id', Integer(), primary_key=True)
    value = Column(String(10))  # shared file, add friend, new message


metadata = Base.metadata

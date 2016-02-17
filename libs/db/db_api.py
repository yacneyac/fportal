#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from libs.conf import DB_USER, DB_PASS, DB_HOST, DB_NAME

engine = create_engine('mysql://%s:%s@%s/%s' % (DB_USER, DB_PASS, DB_HOST, DB_NAME))
Session = sessionmaker(bind=engine)


class DataBaseAPI(object):
    """ API for work with database """
    def __init__(self, table=None):
        self.engine = engine
        self.table = table
        self.sql = ''
        self.params = {}
        self.default_sort = ''
        self.search_fields = []

        self.text = text
        self.session = Session()

    def search(self):
        pass

    def get_obj(self, flt_by, from_table=None):
        db_view = self.session.query(from_table or self.table).filter(flt_by).first()
        self.session.close()
        return db_view

    def get_all(self, flt_by):
        db_view = self.session.query(self.table).filter(flt_by).all()
        self.session.close()
        return db_view

    def delete(self, db_obj):
        self.session.delete(db_obj)
        self.commit()

    def delete_by_filter(self, flt_by):
        self.session.query(self.table).filter(flt_by).delete(synchronize_session='fetch')
        self.commit()

    def create(self, db_obj, commit=True):
        self.session.add(db_obj)
        if commit:
            self.commit()

    def update(self, db_obj):
        self.create(db_obj)

    def update_field(self, flt_by, update_dict):
        self.session.query(self.table).filter(flt_by).update(update_dict, synchronize_session='fetch')
        self.commit()

    def commit(self):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def flush(self):
        self.session.flush()

    def refresh(self, db_obj):
        self.session.refresh(db_obj)

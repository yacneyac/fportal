# -*- encoding: UTF-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""
from tornado.web import HTTPError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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

    def get_by_id_or_404(self, _id, from_table=None):
        obj = self.get_obj('id="%s"' % _id, from_table)

        if obj is None:
            msg = 'object id={id} is not found in DB "{table}"'.format(id=_id, table=from_table or self.table)
            raise HTTPError(404, msg)
        return obj

    def get_obj(self, flt_by, from_table=None):
        return self.session.query(from_table or self.table).filter(flt_by).one_or_none()
        # except MultipleResultsFound:
        #     pass

    def get_all(self, flt_by):
        db_view = self.session.query(self.table).filter(flt_by).all()
        # self.session.close()
        return db_view

    def delete(self, db_obj):
        self.session.delete(db_obj)
        # if commit:
        #     self.commit()

    def delete_by_id(self, _id, from_table=None):
        self.delete(self.get_by_id_or_404(_id, from_table=from_table))

    def delete_by_filter(self, flt_by):
        self.session.query(self.table).filter(flt_by).delete(synchronize_session='fetch')
        # if commit:
        #     self.commit()

    def create(self, db_obj):
        self.session.add(db_obj)
        # if commit:
        #     self.commit()

    # def update(self, db_obj):
    #     self.create(db_obj)

    def update_field(self, flt_by, update_dict):
        self.session.query(self.table).filter(flt_by).update(update_dict, synchronize_session='fetch')
        # if commit:
        #     self.commit()

    def execute(self, sql):
        """Execute raw query"""
        with self.engine.connect() as conn:
            if isinstance(sql, (list, tuple)):
                results = map(conn.execute, sql)
                return [map(dict, res) for res in results]
            return map(dict, conn.execute(sql))

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

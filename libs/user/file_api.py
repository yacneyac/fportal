# -*- coding: utf-8 -*-
"""
Propose: 
Author: 'yac'
Date: 
"""

import os
# from zipfile import ZipFile, ZIP_DEFLATED
# from tempfile import SpooledTemporaryFile
# from contextlib import closing
from datetime import datetime

from libs.models import FileDB, FileShareDB
from libs.conf import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from libs.db.db_api import DataBaseAPI
from libs.portal_exeption import PForbidden
from libs.logger import ac as log
from user_api import UserAPI
from notification_api import NotificationAPI
note = NotificationAPI()

DATE_FORMAT = '%d-%m-%Y %H:%M'
SERVER_ERROR = {'success': False, 'errorMessage': 'server_error'}

# TODO del share file when friend is over
# todo del from share file table when file was delete
# todo check modify on del


class ShareFile(object):
    """ Share file with friends """

    def __init__(self, current_user, file_id, **kwargs):
        self.params = kwargs
        self.file_id = file_id
        self.db = DataBaseAPI(FileShareDB)
        self.current_user = current_user

    def share_file(self):
        """ Share file """
        if not self._permission():
            raise PForbidden

        # get all shared files for current user
        shared_files = self.db.get_all('file_id={current_file_id} and user_own_id={current_user_id}'.format(
            current_file_id=self.file_id,
            current_user_id=self.current_user.id
        ))

        # remove user from shared file
        for s_file in shared_files:
            if s_file.user_assigned_id not in [user['id'] for user in self.params['shared_list']]:
                self.db.delete(s_file)

        for user in self.params['shared_list']:
            if user['id'] not in [s_file.user_assigned_id for s_file in shared_files]:

                file_share = FileShareDB()
                file_share.file_id = self.file_id
                file_share.user_assigned_id = user['id']
                file_share.user_own_id = self.current_user.id
                file_share.date_shared = datetime.now().strftime("%d-%m-%Y %H:%M")
                file_share.permission = user.get('permission', 1)

                self.db.create(file_share)

                # notification
                msg = '%s has been shared file: %s' % (self.current_user.login, self.params['file_name'])
                note.send(self.current_user.id, user['id'], note.SHARE_DOCUMENT, msg)
                log.debug('Notification has been send. \n%s', msg)

        self.db.commit()
        return {'success': True}

    # def get_assigned_user(self, file_id):
    #     """ Get users which assigned to file """
    #     file_list = self.db.get_all('file_id="%s"' % file_id)
    #     return [{'id': db_obj.user_assigned_id, 'text': 'user1  1ds'} for db_obj in file_list]

    def share(self):
        """ Get list of friends and list of assigned friends to file"""
        friend_sql = self.db.text("SELECT u.id, concat(u.second_name, ' ', u.first_name) text FROM user u "
                                  "inner join friend f on f.friend_id=u.id where f.user_id =%s "
                                  "and f.status = 1" % self.current_user.id)
        share_sql = self.db.text("SELECT fs.user_assigned_id id, "
                                 "concat(u.first_name, ' ', COALESCE(u.second_name, '')) text "
                                 "FROM file_share fs inner join user u on u.id = fs.user_assigned_id "
                                 "where fs.file_id = %s" % self.file_id)

        friend_db_list, share_db_list = self.db.execute([friend_sql, share_sql])
        return {'success': True,
                'friend_list': friend_db_list,
                'shared_list': share_db_list}

    def _permission(self):
        file_db = self.db.get_by_id_or_404(self.file_id, from_table=FileDB)
        if int(file_db.user_id) == int(self.current_user.id):
            return True
        return False


class FileAPI(object):
    """ Upload and Download file's API """

    def __init__(self, current_user, file_id=None, **kwargs):

        self.current_user = current_user
        self.file_db = None
        self.params = kwargs

        self.file_dir = os.path.join(UPLOAD_FOLDER, self.current_user.login)
        self.db = DataBaseAPI(FileDB)

        if file_id:
            self.file_db = self.db.get_by_id_or_404(file_id)

        # user api
        self.user_api = UserAPI(self.current_user)
        # self.used_file_quota = self.user_api.user_db.used_file_quota
        # self.file_quota = self.user_api.user_db.file_quota

    # def to_zip(self):
    #     """ Convert file(s) to zip on fly """
    #     file_list = self.db.get_all('id in (%s)' % ','.join((self.params['fileId'])))
    #
    #     log.debug('Convert file(s) to .zip')
    #
    #     with SpooledTemporaryFile() as tempfile:
    #         with closing(ZipFile(tempfile, 'w', ZIP_DEFLATED)) as archive:
    #             for f in file_list:
    #                 archive.write(f.path, arcname=f.name)
    #
    #         tempfile.seek(0)
    #
    #         while True:
    #             _buffer = tempfile.read(4096)
    #             if _buffer:
    #                 yield _buffer
    #             else:
    #                 break

    def update_name(self):
        self.db.update_field('id=%s' % self.params['id'], {'name': self.params['new_name']})
        self.db.commit()

    def upload(self, file_obj):
        """ Save file in FileSystem and save in DB
        :param file_obj: file object for upload
         """
        file_path = ''
        file_name = file_obj.filename
        file_class, file_type = file_obj.content_type.split('/')

        def allowed_file():
            return '.' in file_name and file_name.split('.')[1] in ALLOWED_EXTENSIONS

        try:
            log.debug('Try to save file <%s> for user ID: %s', file_name, self.current_user.login)

            if not allowed_file():
                log.debug('Filetype not allowed')
                return {'success': False, 'errorMessage': 'Filetype not allowed'}

            upload_dir = os.path.join(UPLOAD_FOLDER, self.current_user.login)
            file_path = os.path.join(upload_dir, file_name)

            if os.path.isfile(file_path):
                log.debug('File was uploaded already')
                return {'success': False, 'errorMessage': 'File was uploaded already'}

            if not os.path.exists(upload_dir):
                log.debug('--> Create path: %s', upload_dir)
                os.makedirs(upload_dir)

            # save in File System
            with open(file_path, "ab") as f:
                data = file_obj.body
                f.write(bytes(data))

            os_f_size = os.stat(file_path).st_size

            # check file quota
            if (self.user_api.user_db.used_file_quota + os_f_size) > self.user_api.user_db.file_quota:
                os.remove(file_path)
                log.error('You don\'t have empty space!')
                return {'success': False, 'errorMessage': 'You don\'t have empty space!'}

            file_db = FileDB()
            file_db.name = file_name
            file_db.type = file_type
            file_db.f_class = file_class
            file_db.size = os_f_size
            file_db.user_id = self.current_user.id
            file_db.date_load = datetime.now().strftime(DATE_FORMAT)

            self.db.create(file_db)

            log.debug('--> File has been updated in DB.')

            # update user
            self.user_api.user_db.used_file_quota += os.stat(file_path).st_size  # bytes
            #self.user_api.db.update(self.user_api.user_db)

            self.db.commit()
            self.user_api.db.commit()

            log.debug('--> User in DB has been updated.')

            return {'success': True, 'id': file_db.id}
        except StandardError:
            self.db.session.rollback()
            if os.path.isfile(file_path):
                log.error('File <%s> has been deleted', file_path)
                os.remove(file_path)
            log.exception('Cannot upload file')
            return SERVER_ERROR

    def exist(self):
        return os.path.isfile(os.path.join(self.get_upload_dir(), self.file_db.name))

    def get_upload_dir(self):
        if self.params.get('shared_by'):
            return os.path.join(UPLOAD_FOLDER, self.params['shared_by'])
        return os.path.join(UPLOAD_FOLDER, self.current_user.login)

    def read(self):
        """ Get file """
        file_path = os.path.join(self.get_upload_dir(), self.file_db.name)

        log.debug('Read file <%s>', file_path)
        with open(file_path, "rb") as f:
            while True:
                _buffer = f.read(4096)
                if not _buffer:
                    break
                yield _buffer

    def search(self):
        """ Search file by user """
        try:
            log.debug('Search file for user ID: %s', self.current_user.id)

            sql = "select fs.id, fs.name, fs.size, fs.type, fs.date_load, u.id shared_by_id, u.login shared_by_login, "\
                  "concat(u.first_name, ' ', COALESCE(u.second_name, '')) shared_by_name "\
                  "FROM file_store fs inner join file_share fsh on fsh.file_id = fs.id "\
                  "inner join user u on u.id = fsh.user_own_id where fsh.user_assigned_id ={0} "\
                  "union all(select fs.id, fs.name, fs.size, fs.type, fs.date_load, '' shared_by_id, "\
                  "'' shared_by_login, '' shared_by_name " \
                  "FROM file_store fs where fs.user_id ={0})".format(self.current_user.id)

            files = self.db.execute(sql)

            response = {'files': files,
                        'used_quota': self.user_api.user_db.used_file_quota,
                        'quota': self.user_api.user_db.file_quota,
                        'total': len(files),
                        'extends': list(set(fl['type'] for fl in files))}

            return {'success': True, 'result': response}

        except StandardError:
            log.exception('Cannot search file')
            return SERVER_ERROR

    def delete(self):
        """ Delete file """
        log.debug('Delete file <%s> for user ID: %s', self.file_db.id, self.current_user.login)

#        if not self.can_delete:
#            raise PForbidden

        # check shared file
        # todo send message for users when file is deleted
        shared_file_db = self.db.get_obj('file_id="%s"' % self.file_db.id, from_table=FileShareDB)

        if shared_file_db is not None:
            log.error('File "%s" is shared' % self.file_db.name)
            return {'success': False, 'errorMessage': 'File "%s" is shared' % self.file_db.name}

        if not self.file_db:
            log.error('File <%s> not found in DB', self.file_db.name)
            return {'success': False, 'errorMessage': 'File not found in db'}

        file_path = os.path.join(self.file_dir, self.file_db.name)

        if not os.path.exists(file_path):
            log.error('File <%s> not found in server', file_path)
            return {'success': False, 'errorMessage': 'File not found in server'}

        self.db.delete(self.file_db)
        self.user_api.user_db.used_file_quota -= self.file_db.size

        try:
            os.remove(file_path)
        except StandardError, err:
            self.db.session.rollback()
            self.user_api.db.session.rollback()
            return {'success': False, 'errorMessage': str(err)}

        log.debug('--> File has been deleted.')


        # self.user_api.user_db.used_file_quota -= self.file_db.size
        #self.user_api.db.update(self.user_api.user_db)

        self.db.commit()
        self.user_api.db.commit()

        log.debug('--> User in DB has been updated.')
        return {'success': True}

    # def __permission(self):
    #     file_db = self.db.get_obj('id="%s"' % self.file_obj.file_id)
    #     if file_db.user_id == self.current_user.id:
    #         self.can_delete = True
    #         return True
    #
    #     log.debug('Check shared file.')
    #     select = self.db.text("select fs.user_id owner, fsh.user_assigned_id, fsh.permission from file_store fs "
    #                           "inner join file_share fsh on fsh.file_id = fs.id "
    #                           "where fs.id = %s" % self.file_obj.file_id)
    #     db_response = self.db.engine.execute(select)
    #
    #     shared_file = {}
    #     for db_obj in db_response:
    #         shared_file['owner'] = db_obj[0]
    #         shared_file['user_assigned_id'] = db_obj[1]
    #         shared_file['permission'] = db_obj[2]
    #
    #     if not shared_file:
    #         log.error('File is missing in file share')
    #         return False
    #
    #     # check shared file on current user
    #     if int(shared_file['user_assigned_id']) != int(self.current_user.id):
    #         return False
    #
    #     log.debug('Check friend')
    #     select = self.db.text("select f.status from friend f "
    #                           "where f.user_id =%s and f.friend_id =%s" % (shared_file['owner'], self.current_user.id))
    #     db_response = self.db.engine.execute(select)
    #
    #     friend = [db_obj[0] for db_obj in db_response][0]
    #     if not int(friend):
    #         return False
    #
    #     if shared_file['permission'] != 2:
    #         log.debug('User has permission on modify')
    #         self.can_delete = True
    #
    #     return True

# def convert_size(size):
#     if size:
#         size_name = {1: 'Kb', 2: 'Mb', 3: 'Gb'}
#         i = int(math.floor(math.log(int(size), 1024)))
#         p = math.pow(1024, i)
#
#         s = round(int(size)/p, 2)
#
#         if s > 0:
#             return '%s %s' % (s, size_name[i])
#
#     return '0B'

from tornado.web import authenticated, HTTPError


from .base_handler import BaseHandler
from .file_api import FileAPI, ShareFile


class FileHandler(BaseHandler):
    """ File handler api """
    file = None

    # def prepare(self):
    #     self.file = FileAPI(self.current_user, self.params)
    #
    @authenticated
    def get(self, **kwargs):

        # file to zip
        # if self.params['action'] == 'zf':
        #
        #     file_api = FileAPI(self.current_user)
        #     file_api.params = self.params
        #
        #     self.set_header('Content-Type', 'application/octet-stream')
        #     self.set_header('Content-Disposition', 'attachment; filename=files.zip')
        #
        #     for chunk in file_api.to_zip():
        #         if chunk:
        #             self.write(chunk)
        #
        #     self.finish()
        #     return
        file_id = kwargs['file_id']

        # download
        if self.params['action'] == 'df':
            self.file = FileAPI(self.current_user, file_id, **self.params)

            if not self.file.exist():
                return self.finish({'success': False, 'errorMessage': 'File not exist'})

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + self.file.file_db.name)

            map(self.write, self.file.read())
            self.finish()
            return

        # search
        if self.params['action'] == 'sf':
            self.finish(FileAPI(self.current_user).search())

    @authenticated
    def post(self, **kwargs):
        # upload
        f_obj = self.request.files.get('file')
        if f_obj:
            self.finish(FileAPI(self.current_user).upload(f_obj[0]))
            return

        if 'file_id' in kwargs:
            self.finish(FileAPI(self.current_user, kwargs['file_id'], **self.params).update_name())

    @authenticated
    def delete(self, **kwargs):
        if 'file_id' in kwargs and not self.request.body:
            self.finish(FileAPI(self.current_user, kwargs['file_id']).delete())


class FileShareHandler(BaseHandler):

    @authenticated
    def get(self, **kwargs):
        self.finish(
            ShareFile(self.current_user, kwargs['file_id']).share()
        )

    @authenticated
    def post(self, **kwargs):
        self.finish(
            ShareFile(self.current_user, kwargs['file_id'], **self.params).share_file()
        )

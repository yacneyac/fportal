﻿(function () {
    'use strict';

    angular
        .module('app')
        .factory('UserService', UserService);

    UserService.$inject = ['$http', '$rootScope', 'FileUploader'];
    function UserService($http, $rootScope, FileUploader) {

        var service = {};

        service.uploadFile = uploadFile;
        service.renameFile = renameFile;
        service.DownloadFile = DownloadFile;
        service.deleteFile = deleteFile;
        service.getFileShare = getFileShare;
        service.setFileShare = setFileShare;
        service.GetFiles = GetFiles;

        service.GetByUsername = GetByUsername;
        service.Update = Update;
        service.Auth = Auth;
        service.ChangePicture = ChangePicture;
        service.Create = Register;

        service.GetEvents = GetEvents;
        service.createEvent = createEvent;
        service.deleteEvent = deleteEvent;

        service.getFriends = getFriends;
        //service.getLikelyFriends = getLikelyFriends;
        service.setFriendGroup = setFriendGroup;
        service.actionFriend= actionFriend;


        return service;

        function GetByUsername(username) {
            return $http.get('/user/' + username).then(handleSuccess, handleServerError);
        }

        function GetFiles() {
            var username = $rootScope.globals.currentUser.username;
            return $http.get('/user/' + username + '/file?action=sf').then(handleSuccess, handleServerError);
        }
        function DownloadFile(url) {
            return $http.get(url).then(handleSuccess, handleServerError);
        }
        function uploadFile(){
            var username = $rootScope.globals.currentUser.username;
            $rootScope.uploader = new FileUploader({
                url: '/user/' + username + '/file'
            });
        }
        function renameFile(fileId, data){
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/'+username+'/file/'+fileId, data).then(handleSuccess, handleServerError);
        }
        function deleteFile(fileId) {
            var username = $rootScope.globals.currentUser.username;
            return $http.delete('/user/'+username+'/file/'+fileId).then(handleSuccess, handleServerError);
        }

        function getFileShare(fileId) {
            var username = $rootScope.globals.currentUser.username;
            return $http.get('/user/'+username+'/file/'+fileId+'/share').then(handleSuccess, handleServerError);
        }

        function setFileShare(fileId, data) {
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/'+username+'/file/'+fileId+'/share', data).then(handleSuccess, handleServerError);
        }

        function getFriends(action) {
            var url = '/user/'+ $rootScope.globals.currentUser.username+'/friend?action=' + action;
            return $http.get(url).then(handleSuccess, handleServerError);
        }
        //function getLikelyFriends() {
        //    var url = '/user/' + $rootScope.globals.currentUser.username + '/friend?action=l';
        //    return $http.get(url).then(handleSuccess, handleServerError);
        //}
        function setFriendGroup(friendId, data) {
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/'+username+'/friend/'+friendId, data).then(handleSuccess, handleServerError);
        }

        function actionFriend(friendId, data) {
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/' + username + '/friend/' + friendId, data).then(handleSuccess, handleServerError);
        }


        function GetEvents() {
            var username = $rootScope.globals.currentUser.username;
            return $http.get('/user/' + username + '/calendar').then(handleSuccess, handleServerError);
        }
        function createEvent(data) {
            var username = $rootScope.globals.currentUser.username;
            var url = '/user/' + username + '/calendar';

            if (data.id){
                url = '/user/' + username + '/calendar/' + data.id
                return $http.post(url, data).then(handleSuccess, handleServerError);
            }

            return $http.put(url, data).then(handleSuccess, handleServerError);
        }
        function deleteEvent(eventId) {
            var username = $rootScope.globals.currentUser.username;
            return $http.delete('/user/'+username+'/calendar/'+eventId).then(handleSuccess, handleServerError);
        }

        function ChangePicture(data) {
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/' + username + '/avatar', data).then(handleSuccess, handleServerError);
        }

        function Register(user) {
            return $http.post('/register', user).then(handleSuccess, handleServerError);
        }
        function Update(user) {
            var username = $rootScope.globals.currentUser.username;
            return $http.post('/user/' + username, user).then(handleSuccess, handleServerError);
        }

        function Auth(username, password) {
            return $http.post('/', {username: username, password: password}).then(handleSuccess, handleServerError)
        }


        function handleSuccess(res) {
            return res.data;
        }

        function handleServerError(res){
            return res.data;
        }
    }

})();

(function () {
    'use strict';

    angular.module('app')
        .controller('ProfileController', ProfileController);

    ProfileController.$inject = ['UserService', 'FlashService', '$rootScope', '$filter'];

    function ProfileController(UserService, FlashService, $rootScope) {

        $rootScope.Loading = false;
        $rootScope.updateInfo = function (user, form){

            $rootScope.Loading = true;
            form.$setPristine();

            if (user.info.birthday)
                user.info.birthday = new Date(user.info.birthday).getTime();

            UserService.Update(user.info).then(function (response) {

                if (response.success){
                    $rootScope.Loading = false;
                    FlashService.Success('Information updated!');
                }
                else {
                    $rootScope.Loading = false;
                    FlashService.Error(response.errorMessage);
                }
            });
        };

        /////////////DATAPICKER///////////////
        $rootScope.minDate = new Date(1970, 1, 1);
        $rootScope.maxDate = new Date();
        $rootScope.dateOptions = {
            startingDay: 1
        };

        $rootScope.open = function($event) {
            $rootScope.status.opened = true;
        };

        $rootScope.status = {
            opened: false
        };

        //////PERMISSION//
        $rootScope.updatePermission = function(form){
            $rootScope.Loading = true;
            form.$setPristine();
            UserService.Update($rootScope.user.permission).then(function (response) {

                if (response.success){
                    $rootScope.Loading = false;
                    FlashService.Success('Information updated!');
                }
                else {
                    $rootScope.Loading = false;
                    FlashService.Error(response.errorMessage);
                }
            });
        };

        ////////////////CHANGE PASSWORD //////
        $rootScope.changePassword = function (user, form){
            $rootScope.Loading = true;
            $rootScope.reset(form);

            UserService.Update(user.security).then(function (response) {

                if (response.success){
                    $rootScope.Loading = false;
                    FlashService.Success('Password has been changed!');
                }
                else {
                    $rootScope.Loading = false;
                    FlashService.Error(response.errorMessage);
                }
            });
        };
        $rootScope.reset = function (form){
            $rootScope.user = {'password': null,
                               'newpassword': null,
                               'confpassword': null};
            form.$setPristine();
        };
    }
})();
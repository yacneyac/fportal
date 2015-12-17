(function () {
    'use strict';

    angular
        .module('app')
        .controller('RegisterController', RegisterController);

    RegisterController.$inject = ['UserService', '$location', '$rootScope', 'FlashService'];
    function RegisterController(UserService, $location, FlashService) {
        var vm = this;

        vm.register = register;

        function register() {
            vm.dataLoading = true;

            UserService.Create(vm.user).then(function (response) {
                if (response.success) {
                    FlashService.Success('Registration successful');
                    $location.path('/login');
                } else {
                    FlashService.Error(response.errorMessage);
                    vm.dataLoading = false;
                    vm.user.password = '';
                    vm.user.confpassword = '';
                }
            });
        }
    }

})();

angular.module('app').controller('LoginController',
    function ($rootScope, $location, FlashService, AuthenticationService) {

        var vm = this;

        vm.login = login;

        (function initController() {
            // reset login status
            AuthenticationService.ClearCredentials();
        })();

        function login() {
            vm.dataLoading = true;
            AuthenticationService.Login(vm.username, vm.password, function (response) {
                if (response.success) {
                    AuthenticationService.SetCredentials(vm.username, vm.password);
                    $location.path('/home');
                } else {
                    FlashService.Error(response.errorMessage);
                    vm.dataLoading = false;
                }
            });
        }
    }
);

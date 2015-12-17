(function () {
    'use strict';

    angular
        .module('app')
        .factory('FlashService', FlashService);

    FlashService.$inject = ['$rootScope'];
    function FlashService($rootScope) {
        var service = {};

        service.Success = Success;
        service.Error = Error;

        initService();

        return service;

        function initService() {
            $rootScope.$on('$locationChangeStart', function () {
                clearFlashMessage();
            });

            function clearFlashMessage() {
                var flash = $rootScope.flash;
                if (flash) {
                    if (!flash.keepAfterLocationChange) {
                        delete $rootScope.flash;
                    } else {
                        // only keep for a single location change
                        flash.keepAfterLocationChange = false;
                    }
                }
            }
        }

        function Success(message) {
            $.notify({
                delay: 2000,
                message: message
            },{
                type: 'success'
            });


            //$rootScope.flash = {
            //    message: message,
            //    type: 'success',
            //    keepAfterLocationChange: keepAfterLocationChange
            //};
        }

        function Error(message) {
            $.notify({
                // options
                title: '<strong>Oops!</strong>',
                message: message,
                delay: 2000
            },{
                // settings
                type: 'danger'
            });
        }
    }

})();
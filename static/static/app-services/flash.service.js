(function () {
    'use strict';

    angular
        .module('app')
        .factory('FlashService', FlashService);

    //FlashService.$inject = [];
    function FlashService() {
        var service = {},
            temp = '<div data-notify="container" class="col-xs-2 alert alert-{0}" role="alert">' +
                '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">&times;</button>' +
                '<span data-notify="icon"></span> <span data-notify="title">{1}</span> ' +
                '<span data-notify="message">{2}</span><div class="progress" data-notify="progressbar">' +
                '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" ' +
                'aria-valuemax="100" style="width: 0%;"></div></div><a href="{3}" target="{4}" ' +
                'data-notify="url"></a></div>';


        service.Success = Success;
        service.Error = Error;


        return service;

        function Success(message) {

            $.notify({
                message: message
            },{
                type: 'success',
                delay: 1000,
                template: temp
            });
        }

        function Error(message) {
            $.notify({
                // options
                title: '<strong>Oops!</strong>',
                message: message
            },{
                // settings
                delay: 2000,
                type: 'danger'
            });
        }
    }

})();
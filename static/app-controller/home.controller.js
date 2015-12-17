(function () {
    'use strict';

    angular.module('app').controller('HomeController', HomeController);
    HomeController.$inject = ['$rootScope', 'UserService', '$route', '$filter'];
    function HomeController($rootScope, UserService, $route, $filter) {

        var defaultMenu = '/static/app-content/settings.view.html';

        $rootScope.setActiveMenu = function(src){
            $rootScope.activeMenu = src;
        };

        $rootScope.menus = [];
        $rootScope.user = {};

        initController();
        function initController() {
            loadCurrentUser();
            $rootScope.activeMenu = defaultMenu;
        }

        function loadCurrentUser() {
            UserService.GetByUsername($rootScope.globals.currentUser.username)
                .then(function (user) {

                    $rootScope.user = user.result;

                    for (var i=0; i<user.result.menu.length; i++){

                        $rootScope.menus.push({
                            name: user.result.menu[i],
                            src: '/static/app-content/' + user.result.menu[i].toLowerCase() + '.view.html'
                        })
                    }

                    if (!user.result.avatar)
                        $rootScope.user.avatarurl = '/static/img/photo.png';
                    else
                        $rootScope.user.avatarurl = '/static/avatar/' + user.result.id + '/'+ user.result.avatar;
                });
        }
    }

})();
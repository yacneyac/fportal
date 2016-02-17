(function () {
    'use strict';

    angular.module('app').controller('HomeController', HomeController);
    HomeController.$inject = ['$rootScope', 'UserService', 'FlashService'];
    function HomeController($rootScope, UserService, FlashService) {

        var defaultMenu = '/static/app-content/settings.view.html';

        $rootScope.setActiveMenu = function (src, name) {
            $rootScope.activeMenu = src;

            var menu = $("#"+name);

            if (menu[0].firstElementChild)
                menu[0].firstElementChild.remove();
        };

        $rootScope.menus = [];
        $rootScope.user = {};

        initController();
        function initController() {
            loadCurrentUser();
            $rootScope.activeMenu = defaultMenu
        }

        function loadCurrentUser() {
            UserService.GetByUsername($rootScope.globals.currentUser.username)
                .then(function (user) {

                    $rootScope.user = user.result;
                    makeWebSocket(user.result.id);

                    for (var i = 0; i < user.result.menu.length; i++) {

                        $rootScope.menus.push({
                            name: user.result.menu[i],
                            src: '/static/app-content/' + user.result.menu[i].toLowerCase() + '.view.html'
                        })
                    }

                    if (!user.result.avatar)
                        $rootScope.user.avatarurl = '/static/img/photo.png';
                    else
                        $rootScope.user.avatarurl = '/static/avatar/' + user.result.id + '/' + user.result.avatar;
                });
        }


        function makeWebSocket(userId) {
            var badgeSuccess = '<span id="{0}-badge" class="badge badge-success" style="margin-left: 5px;">1</span>',
                MSG_MAP = {share_doc: 'Documents'};


            var socket = null;
            var isopen = false;
            var hostname = window.document.location.hostname;

            if (hostname == "localhost" || hostname == "127.0.0.1") {
                socket = new WebSocket("ws://" + hostname + ":8080/ws");
            }
            else {
                socket = new WebSocket("ws://" + hostname + ":8000/ws");
            }

            socket.onopen = function () {
                console.log("Connected!");
                isopen = true;
                socket.send(JSON.stringify({'id': userId }));
            };

            socket.onmessage = function (e) {
                console.log("Text message received: " + e.data);

                var badge = $('a .badge-success'),
                    count = Number(badge.text()),
                    res = JSON.parse(e.data);


                console.log(MSG_MAP[res.msg_type])
                console.log(typeof badgeSuccess)

                if (count == 0)
                    $('#'+MSG_MAP[res.msg_type]).append(badgeSuccess);
                else
                    badge.text(count + 1);

                FlashService.Success(res.msg);
            };

            socket.onclose = function (e) {
                console.log("Connection closed")
                isopen = false;
                socket = null;

                //console.log("Connection closed. Try to reconnect");
                //isopen = false;
                //
                //socket.onopen = function () {
                //    console.log("Connected!");
                //    isopen = true;
                //    socket.send(JSON.stringify({'id': userId }));
                //};
                //
                //if (isopen == false) {
                //    console.log('Connection closed.');
                //    socket = null;
                //}

            };
        }
    }
})();
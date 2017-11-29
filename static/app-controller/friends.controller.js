angular.module('app').controller('FriendsController',
    function ($rootScope, UserService, FlashService, $confirm) {

    var vm = this;

    var content = '/static/app-content/friends.list.html';

    vm.friendTabs = [{'name': 'All Friends', 'sname': 'all_frn', 'isOnline': false, 'content': content},
                     {'name': 'Online', 'sname': 'on_frn', 'isOnline': true, 'content': content},
                     {'name': 'Requests', 'sname': 'req_frn', 'isOnline': null, 'content': content},
                     {'name': 'New Friends', 'sname': 'new_frn', 'isOnline': null, 'hide': true, 'content': content}
    ];

    vm.actions = ['Write a message', 'Friend', 'Unfriend'];
    vm.displayedCollection = [];
    $rootScope.friendsCollection = [];

    getFriends();

    function getFriends(){
        UserService.getFriends('all').then(function (response) {

            if (response.success) {

                generateFriendList(response.friends);

                $rootScope.friendsCollection = response.friends;
                $rootScope.friendsGroup = response.groups;
            }
            else {
                FlashService.Error(response.errorMessage);
            }
        });
    }

    vm.getNewFriends = function(){
        vm.friendTabs[3].hide=false;
        vm.friendTabs[3].active=true;

        UserService.getFriends('new').then(function (response) {

            if (response.success)
                generateFriendList(response.new_friends);
            else
                FlashService.Error(response.errorMessage);
        });
    };

    vm.getRequestsFriends = function(action){
        UserService.getFriends(action).then(function (response) {

            if (response.success)
                generateFriendList(response.r_friends);
            else
                FlashService.Error(response.errorMessage);
        });
    };


    vm.selectedIndex = null;
    vm.isOnline = false;

    vm.setOnline = function(online){
        if (online == null)
            return;

        vm.isOnline = online;
        vm.setFilter(null, null)
    };

    vm.setFilter = function ($index, flt){
        vm.selectedIndex = $index;
        vm.displayedCollection = [];
        var dataSource = $rootScope.friendsCollection;

        if (vm.isOnline)
            dataSource = vm.friendsOnlineCollection;

        if (flt) {
            for (var i = 0; i < dataSource.length; i++) {

                var f_groups = dataSource[i].groups;

                for (var j=0; j<f_groups.length; j++){
                    if (f_groups[j].assigned && f_groups[j].name == flt){
                        vm.displayedCollection.push(dataSource[i])
                    }
                }
            }
        }
        else {
            if (vm.isOnline) {
                vm.friendsOnlineCollection = [];

                for (var k = 0; k < $rootScope.friendsCollection.length; k++) {
                    if ($rootScope.friendsCollection[k].online) {
                        vm.displayedCollection.push($rootScope.friendsCollection[k]);
                        vm.friendsOnlineCollection.push($rootScope.friendsCollection[k]);  // for len in html
                    }
                }
            }
            else
                vm.displayedCollection = [].concat(dataSource)
        }
    };

    vm.hideNewTab = function($index){
        if ($index!=3)
            vm.friendTabs[3].hide=true;

        if ($index==2)
            vm.getRequestsFriends('my_req')
    };

    vm.setGroup = function(assignedGroup, friendId){
        UserService.setFriendGroup(friendId, assignedGroup).then(function (response) {
            if (!response.success)
                FlashService.Error(response.errorMessage);
            else
                assignedGroup.assign_id = response.id;
        });
    };

    vm.addDelFriend = function(action, friend){

        var data = {action: action,
//                    initial_id: friend.initial_id,
                    relation_id: friend.relation_id,
                    groups: friend.groups
        };



        UserService.actionFriend(friend.id, data).then(function (response) {
            if (response.success){

                // todo
                if (action=='add'){
                    $rootScope.friendsCollection.push(friend)
                }
                else {
                    for (var k = 0; k < $rootScope.friendsCollection.length; k++) {
                        if ($rootScope.friendsCollection[k].id == friend.id) {
                            $rootScope.friendsCollection.splice(k, 1);
                            vm.displayedCollection.push($rootScope.friendsCollection[k]);
                        }
                    }
                }
            }
            else
                FlashService.Error(response.errorMessage);
        });

    };


    function generateFriendList(source){
        for (var i=0; i<source.length; i++){
            if (!source[i].avatar)
                source[i].avatarurl = '/static/img/photo.png';
            else
                source[i].avatarurl = '/static/avatar/'+source[i].id+'/'+source[i].avatar;
        }
        vm.displayedCollection = [].concat(source);
    }
});

angular.module('app').directive('clickOff', function($parse, $document) {
    var dir = {
        compile: function($element, attr) {
          // Parse the expression to be executed
          // whenever someone clicks _off_ this element.
            var fn = $parse(attr["clickOff"]);
            return function(scope, element, attr) {
            // add a click handler to the element that
            // stops the event propagation.
                element.bind("click", function(event) {
                    //console.log("stopProp");
                    event.stopPropagation();
                });
                angular.element($document[0].body).bind("click", function(event) {
                    //console.log("cancel.");
                    scope.$apply(function() {
                        fn(scope, {$event:event});
                    });
                });
            };
        }
    };
    return dir;
});
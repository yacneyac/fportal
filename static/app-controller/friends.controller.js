angular.module('app').controller('FriendsController',
    function ($rootScope, UserService, FlashService, $confirm) {

    var vm = this;
    var content = '/static/app-content/friends.list.html';

    vm.friendTabs = [{'name': 'All Friends', 'sname': 'all_frn', 'content': content, 'action': getAllFriends},
                     {'name': 'Requests', 'sname': 'req_frn', 'content': content, 'action': getRequestsFriends},
                     {'name': 'New Friends', 'sname': 'new_frn', 'content': content, 'action': getNewFriends}
    ];

    vm.actions = ['Write a message', 'Friend', 'Unfriend'];
    vm.displayedCollection = [];
    $rootScope.friendsCollection = [];

    getAllFriends();
//    getRequestsFriends();

    function getAllFriends(){
        UserService.getFriends('all').then(function (response) {

            if (response.success) {

                generateFriendAvatar(response.friends);

                $rootScope.friendsCollection = response.friends;
                $rootScope.friendsGroup = response.groups;
            }
            else {
                FlashService.Error(response.errorMessage);
            }
        });
    }

    function getNewFriends(){
//        vm.friendTabs[2].hide=false;
//        vm.friendTabs[2].active=true;

        UserService.getFriends('new').then(function (response) {

            if (response.success)
                 generateFriendAvatar(response.new_friends);
            else
                FlashService.Error(response.errorMessage);
        });
    };
    vm.getNewFriends = getNewFriends

    function getRequestsFriends(){
        UserService.getFriends('my_req').then(function (response) {

            if (response.success){
                    generateFriendAvatar(response.r_friends);
//                    vm.friendTabs[1].hide=false;
                }
            else
                FlashService.Error(response.errorMessage);
        });
    };

    // TODO: ng-class in html
    vm.setFilter = function (flt){
        vm.displayedCollection = [];
        var friendsSource = $rootScope.friendsCollection;

        if (flt == 'online'){
            for (var i = 0; i < friendsSource.length; i++) {
                if (friendsSource[i].online){
                    vm.displayedCollection.push(friendsSource[i])
                }
            }
        }
        else if (flt=='clear') {
            vm.displayedCollection = friendsSource
        }

        // make filter by group
        else {
            var filter_group_name = flt;

            for (var i = 0; i < friendsSource.length; i++) {

                var f_groups = friendsSource[i].groups

                for (var j=0; j<f_groups.length; j++){
                    if (f_groups[j].assigned && f_groups[j].name == filter_group_name){
                        vm.displayedCollection.push(friendsSource[i])
                    }
                }
            }
        }
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

                    for (var k = 0; k < vm.displayedCollection.length; k++) {

                        if (vm.displayedCollection[k].id == friend.id)

//                            $rootScope.friendsCollection.push(friend)

                            vm.displayedCollection.splice(k, 1);
                    }


                }
                // remove from displayedCollection
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


    function generateFriendAvatar(source){
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
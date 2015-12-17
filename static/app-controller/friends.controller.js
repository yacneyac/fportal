angular.module('app').controller('FriendsController', function ($rootScope, UserService, FlashService, $confirm) {

    var vm = this;

    vm.actions = ['Write a message', 'Unfriend'];
    vm.displayedCollection = [];
    $rootScope.friendsCollection = [];

    getFriends();

    function getFriends(){
        UserService.getFriends().then(function (response) {

            if (response.success) {

                for (var i=0; i<response.friends.length; i++){
                    if (!response.friends[i].avatar)
                        response.friends[i].avatarurl = '/static/img/photo.png';
                    else {
                        response.friends[i].avatarurl = '/static/avatar/' + response.friends[i].id + '/'
                            + response.friends[i].avatar;

                        response.friends[i].online = true;

                    }
                }

                $rootScope.friendsCollection = response.friends;
                vm.displayedCollection = [].concat($rootScope.friendsCollection);
            }
            else {
                FlashService.Error(response.errorMessage);
            }
        });
    }


    vm.setGroup = function(assignedGroup, friendId){
        assignedGroup.friend_id = friendId;

        UserService.setFriendGroup(assignedGroup).then(function (response) {
            if (!response.success)
                FlashService.Error(response.errorMessage);
        });
    };
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
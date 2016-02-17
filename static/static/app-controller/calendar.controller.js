angular.module('app').controller('CalendarController', function ($rootScope, $route, UserService,
                                                                 FlashService, $uibModal, $confirm) {

    var vm = this;

    $rootScope.types = ['info', 'important', 'warning', 'success'];
    $rootScope.recurs = ['year', 'month'];
    $rootScope.calendarEvent = {};

    vm.calendarView = 'month';
    vm.calendarDay = new Date();
    vm.events = [];
    vm.isCellOpen = true;

    loadEvents();

    function loadEvents() {
        UserService.GetEvents().then(function (response) {
            if (response.success){

                for (var i=0; i<response.result.length; i++){
                    var eventObj = {
                        title: response.result[i].title,
                        type: response.result[i].event_class,
                        startsAt: new Date(response.result[i].start_at*1000),
                        id: response.result[i].id
                    };

                    if (response.result[i].end_at)
                        eventObj.endsAt = new Date(response.result[i].end_at*1000);

                    if (response.result[i].recurs_on)
                        eventObj.recursOn = response.result[i].recurs_on;

                    vm.events.push(eventObj)
                }
            }
            else
                FlashService.Error(response.errorMessage);
        })
    }
    ///////// DATETIME PICKER /////
    $rootScope.startDate = new Date();
    $rootScope.startStatus = {
        opened: false
    };
    $rootScope.endStatus = {
        opened: false
    };
    $rootScope.dateOptions = {
        startingDay: 1
    };
    $rootScope.timeOptions = {
        showMeridian: false,
        minuteStep: 15
    };

    $rootScope.dateOpen = function($event, action) {
        if (action == 'start')
            $rootScope.startStatus.opened = true;
        else
            $rootScope.endStatus.opened = true;
    };

    $rootScope.hideStart = false;
    $rootScope.hideEnd = true;

    $rootScope.showDateTime = function(action){
        $rootScope.hideStart = ! $rootScope.hideStart;
        $rootScope.hideEnd = ! $rootScope.hideEnd;

        clearEndError();
        if (action == 'setStart')
            $rootScope.actionEvent.endsAt = null;
        else
            setEndDate();
    };

    $rootScope.onChangeStartDate = function(){
        $rootScope.isStartError = false;
        $rootScope.endStartMsg = '';

        if (!$rootScope.actionEvent.startsAt){
            $rootScope.isStartError = true;
            $rootScope.endStartMsg = 'The start time is required!';
        }

        if ($rootScope.actionEvent.endsAt){
            clearEndError();
            setEndDate()
        }
    };

    $rootScope.onChangeEndDate = function(){
        clearEndError();

        if ($rootScope.actionEvent.endsAt) {
            var start = $rootScope.actionEvent.startsAt.getTime();
            var end = $rootScope.actionEvent.endsAt.getTime();

            if (start >= end) {
                $rootScope.isEndError = true;
                $rootScope.endErrMsg = 'The event end time must be after the start time.';
            }
        }
        else {
            $rootScope.isEndError = true;
            $rootScope.endErrMsg = 'End time is incorrect';
        }
    };

    function clearEndError(){
        $rootScope.isEndError = false;
        $rootScope.endErrMsg = '';
    }

    function setEndDate(){
        if ($rootScope.actionEvent.startsAt) {
            var startDate = new Date($rootScope.actionEvent.startsAt.getTime());
            startDate.setHours(startDate.getHours() + 2);

            $rootScope.actionEvent.endsAt = null;
            $rootScope.actionEvent.endsAt = startDate;
        }
    }

//////////////////////////////////////////////////////////////////////////////////
    function openEventModal(action, event) {
        var modalEventInstance = $uibModal.open({
            templateUrl: 'modalEventContent.html',
            animation: true,
            size: 'sm',
            controller: function() {
                var vm = this;
                vm.action = action;

                if (action == 'Create'){
                    $rootScope.hideStart = false;
                    $rootScope.hideEnd = true;

                    $rootScope.actionEvent = {
                        startsAt: new Date(),
                        type: 'info'
                    };
                }
                else {
                    $rootScope.actionEvent = jQuery.extend({}, event);

                    if (event.endsAt){
                         $rootScope.hideEnd = false;
                         $rootScope.hideStart = true;
                    }
                }
            },
            controllerAs: 'vm'
        });

        $rootScope.modalEventInstance = modalEventInstance;

        modalEventInstance.result.then(function () {

            var sendEvent = jQuery.extend({}, $rootScope.actionEvent);
            var startDateInMil = new Date($rootScope.actionEvent.startsAt).getTime();

            sendEvent.startsAt = Math.floor(startDateInMil/1000);

            if ($rootScope.actionEvent.endsAt){
                var endDateInMil = new Date($rootScope.actionEvent.endsAt).getTime();
                sendEvent.endsAt = Math.floor(endDateInMil/1000);
            }

            UserService.createEvent(sendEvent).then(function (response) {

                if (!response.success){
                    FlashService.Error(response.errorMessage);
                }
                // insert event to events_list
                else {
                    if ($rootScope.actionEvent.id){

                        for (var i=0; i<vm.events.length; i++){

                            if ($rootScope.actionEvent.id == vm.events[i].id){

                                vm.events[i].title = $rootScope.actionEvent.title;
                                vm.events[i].type = $rootScope.actionEvent.type;
                                vm.events[i].startsAt = new Date(startDateInMil);

                                if ($rootScope.actionEvent.recursOn)
                                    vm.events[i].recursOn = $rootScope.actionEvent.recursOn;
                                else
                                    delete vm.events[i].recursOn;

                                if ($rootScope.actionEvent.endsAt)
                                    vm.events[i].endsAt =  new Date(endDateInMil);
                                else
                                    delete vm.events[i].endsAt;
                            }
                        }
                    }
                    else {
                        var eventObj = {
                            title: $rootScope.actionEvent.title,
                            type: $rootScope.actionEvent.type,
                            startsAt: new Date(startDateInMil),
                            id: response.id
                        };

                        if ($rootScope.actionEvent.recursOn)
                            eventObj.recursOn = $rootScope.actionEvent.recursOn;

                        if ($rootScope.actionEvent.endsAt)
                            eventObj.endsAt = new Date(endDateInMil);

                        vm.events.push(eventObj)
                    }
                }
            });
        }, function () {});
    }


    vm.eventClicked = function(event) {
        $rootScope.btnName = 'Update';
        openEventModal('View', event);
    };

    $rootScope.deleteEvent = function(event){
        delEvent(event);
        $rootScope.modalEventInstance.close()
    };

    vm.eventDeleted = function(event) {
        $confirm({text: 'Are you sure you want to delete?', ok: 'Yes', cancel: 'No'})
        .then(function() {
            delEvent(event)
        });
    };

    function delEvent(event){
        UserService.deleteEvent(event.id).then(function (response) {
            if (response.success){
                for (var i=0; i<vm.events.length; i++){
                    if (event.id == vm.events[i].id)
                        vm.events.splice(i, 1);
                }
            }
            else
                FlashService.Error(response.errorMessage);
        });
    }

    vm.createEvent = function(){
        $rootScope.btnName = 'Create';
        openEventModal('Create', '')

    };
});

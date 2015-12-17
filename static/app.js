(function () {
    'use strict';

    angular
        .module('app', ['ngRoute', 'ngCookies', 'ng.confirmField', 'ui.bootstrap', 'ngAnimate',
                        'ngImgCrop', 'smart-table', 'angularFileUpload', 'angular-confirm',
                        'frapontillo.bootstrap-duallistbox', 'mwl.calendar', 'ui.bootstrap.datetimepicker'])
        .config(appConfig)
        .run(run);

    //appConfig.$inject = ['$routeProvider', '$locationProvider'];
    function appConfig($routeProvider, calendarConfigProvider) {

        moment.locale('uk', {
              week : {
                dow : 1 // Monday is the first day of the week
              }
            });
        //moment().format('LL');
        //
        calendarConfigProvider.setDateFormatter('moment');
        //  calendarConfigProvider.setDateFormats({
        //      hour: 'HH:mm' // this will configure times on the day view to display in 24 hour format rather than the default of 12 hour
        //    });
        //  calendarConfigProvider.setTitleFormats({
        //      day: 'ddd D MMM' //this will configure the day view title to be shorter
        //    });


        $routeProvider
            //.when('/home/:user_id?', {
            //    controller: 'HomeController',
            //    templateUrl: '/static/app-content/home.view.html',
            //    controllerAs: 'vm'
            //})
            .when('/home', {
                controller: 'HomeController',
                templateUrl: '/static/app-content/home.view.html',
                controllerAs: 'vm'
            })

            .when('/login', {
                controller: 'LoginController',
                templateUrl: '/static/app-content/login.view.html',
                controllerAs: 'vm'
            })

            .when('/register', {
                controller: 'RegisterController',
                templateUrl: '/static/app-content/register.view.html',
                controllerAs: 'vm'
            })

            .otherwise({ redirectTo: '/login' });
    }

    run.$inject = ['$rootScope', '$location', '$cookieStore', '$http'];
    function run($rootScope, $location, $cookieStore, $http) {
        // keep user logged in after page refresh
        $rootScope.globals = $cookieStore.get('globals') || {};
        if ($rootScope.globals.currentUser) {
            $http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata;
        }

        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            // redirect to login page if not logged in and trying to access a restricted page
            var restrictedPage = $.inArray($location.path(), ['/login', '/register']) === -1;
            var loggedIn = $rootScope.globals.currentUser;
            if (restrictedPage && !loggedIn) {
                $location.path('/login');
            }
        });

    }

})();
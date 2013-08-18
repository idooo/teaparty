define(['angular', 'src/app'], function(angular, app) {
    'use strict';

    // to prevent caching
    var v = "?v=" + (new Date()).getTime();

    return app.config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/', {
            templateUrl: 'templates/main.html' + v,
            controller: 'DashboardController'
        });

        $routeProvider.when('/help', {
            templateUrl: 'templates/help.html' + v
        });

        // $routeProvider.otherwise({redirectTo: '/'});
    }]);

});
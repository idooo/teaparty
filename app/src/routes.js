define(['angular', 'src/app'], function(angular, app) {
    'use strict';

    return app.config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/', {
            // templateUrl: 'app/templates/help.html',
            controller: 'DashboardController'
        });
        $routeProvider.when('/help', {
            templateUrl: 'templates/help.html'
            // controller: 'MyCtrl1'
        });
        $routeProvider.otherwise({redirectTo: '/'});
    }]);

});
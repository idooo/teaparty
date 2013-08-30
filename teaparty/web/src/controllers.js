define(['angular', 'src/services'], function (angular) {
	'use strict';

	var controllers = angular.module('teapartyApp.controllers', ['teapartyApp.services']);

    controllers.controller(
        'DashboardController', ['$scope', '$injector', '$http', 'socket', function($scope, $injector, $http, socket) {
        require(['src/controllers/dashboard'], function(dashctrl) {
            $injector.invoke(dashctrl, this, {'$scope': $scope, '$http': $http, 'socket': socket});
        });
    }]);

    return controllers;
});
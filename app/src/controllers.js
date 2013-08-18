define(['angular', 'src/services'], function (angular) {
	'use strict';

	var controllers = angular.module('teapartyApp.controllers', ['teapartyApp.services']);

    controllers.controller('DashboardController', ['$scope', '$injector', '$http', function($scope, $injector, $http) {
        require(['src/controllers/dashboard'], function(dashctrl) {
            $injector.invoke(dashctrl, this, {'$scope': $scope, '$http': $http});
        });
    }]);

    return controllers;
});
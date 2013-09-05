define([
    'angular',
    'src/services' ,
    'progressbar'

], function (angular) {

	'use strict';

	var controllers = angular.module('teapartyApp.controllers', ['teapartyApp.services', 'ngProgress']);

    controllers.controller(
        'DashboardController', ['$scope', '$injector', '$http', 'socket', 'progressbar',
            function($scope, $injector, $http, socket, progressbar) {
                require(['src/controllers/dashboard'], function(dashctrl) {
                    $injector.invoke(dashctrl, this, {
                        '$scope': $scope, '$http': $http, 'socket': socket, 'progressbar': progressbar
                    });
                });
    }]);

    return controllers;
});
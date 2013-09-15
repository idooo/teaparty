define([
    'angular',
    'src/services' ,
    'progressbar'

], function (angular) {

	'use strict';

	var controllers = angular.module('teapartyApp.controllers', ['teapartyApp.services', 'ngProgress']);

    controllers.controller(
        'DashboardController', ['' +
            '$scope', '$injector', '$http', '$timeout', 'socket', 'progressbar',
            function($scope, $injector, $http, $timeout, socket, progressbar) {
                require(['src/controllers/dashboard'], function(dashctrl) {
                    $injector.invoke(dashctrl, this, {
                        '$scope': $scope,
                        '$http': $http,
                        '$timeout': $timeout,
                        'socket': socket,
                        'progressbar': progressbar,
                    });
                });
    }]);

    return controllers;
});
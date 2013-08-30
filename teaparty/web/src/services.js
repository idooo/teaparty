define(['angular'], function (angular) {
	'use strict';

	var url = '/socket';
	var services = angular.module('teapartyApp.services', []);

    services.factory('socket', function ($rootScope) {
        var socket = io.connect(url);
        return {
            on: function (eventName, callback) {
                socket.on(eventName, function () {
                    var args = arguments;
                    $rootScope.$apply(function () {
                        callback.apply(socket, args);
                    });
                });
            },
            emit: function (eventName, data, callback) {
                socket.emit(eventName, data, function () {
                    var args = arguments;
                    $rootScope.$apply(function () {
                        if (callback) {
                            callback.apply(socket, args);
                        }
                    });
                })
            }
        };
    });
});
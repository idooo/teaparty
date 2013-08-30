define([
    'angular',
    'src/filters',
    'src/services',
    'src/directives',
    'src/controllers'
], function (angular, filters, services, directives, controllers) {
    'use strict';
    return angular.module('teapartyApp', [
        'teapartyApp.controllers',
        'teapartyApp.filters',
        'teapartyApp.services',
        'teapartyApp.directives'
    ]);
});


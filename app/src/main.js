require.config({
    paths: {
        angular: 'lib/angular/angular',
        text: 'lib/require/text'
    },
    baseUrl: '',
    // For dev purposes
    urlArgs: "v=" + (new Date()).getTime(),
    shim: {
        'angular' : {'exports' : 'angular'},
        'angularMocks': {deps:['angular'], 'exports':'angular.mock'}
    },
    priority: [
        "angular"
    ]
});

require( [
    'angular',
    'src/app',
    'src/routes'
], function(angular, app, routes) {
    'use strict';
    angular.bootstrap(document, [app['name']]);
});

require.config({
    paths: {
        underscore: 'lib/underscore/underscore',
        socketio: 'lib/socketio/socket.io',
        angular: 'lib/angular/angular',
        text: 'lib/require/text'
    },

    // prevent caching for dev purposes
    urlArgs: "v=" + (new Date()).getTime(),

    shim: {
        'angular' : {
            'deps': ['underscore', 'socketio'],
            'exports' : 'angular'
        }
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

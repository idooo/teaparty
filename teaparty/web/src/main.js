require.config({
    paths: {
        socketio: 'vendor/socketio/socket.io',
        angular: 'vendor/angular/angular',
        text: 'vendor/require/text',

        // modules
        d3: 'vendor/d3/d3.min',
        progressbar: 'src/components/ngProgress'
    },

    // prevent caching for dev purposes
    urlArgs: "v=" + (new Date()).getTime(),

    shim: {
        'angular' : {
            'deps': ['socketio'],
            'exports' : 'angular'
        },
    },
    priority: [
        "angular",
        "d3"
    ]
});

require( [
    'angular',
    'src/app',
    'src/routes',
    'd3'
], function(angular, app, routes) {
    'use strict';
    angular.bootstrap(document, [app['name']]);
});

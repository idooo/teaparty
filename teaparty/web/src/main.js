require.config({
    paths: {
        socketio: 'vendor/socketio/socket.io',
        angular: 'vendor/angular/angular',
        text: 'vendor/require/text',

        // modules
        d3: 'vendor/d3/d3.min',
        rickshaw: 'vendor/rickshaw',
        momentjs: 'vendor/momentjs/moment',
        progressbar: 'src/components/ngProgress'
    },

    // prevent caching for dev purposes
    urlArgs: "v=" + (new Date()).getTime(),

    shim: {
        'angular' : {
            'deps': ['socketio'],
            'exports' : 'angular'
        }
    },
    priority: [
        "angular",
        "momentjs",
        "d3",
        "rickshaw"
    ]
});

require( [
    'angular',
    'src/app',
    'src/routes',
    'd3',
    'rickshaw'
], function(angular, app, routes) {
    'use strict';
    angular.bootstrap(document, [app['name']]);
});

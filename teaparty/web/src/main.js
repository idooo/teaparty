require.config({
    paths: {
        socketio: 'vendor/socketio/socket.io',
        angular: 'vendor/angular/angular',
        text: 'vendor/require/text',

        // modules
        deadsimple: 'vendor/dead.simple',
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
        "deadsimple"
    ]
});

require( [
    'angular',
    'src/app',
    'src/routes',
    'deadsimple',
], function(angular, app, routes) {
    'use strict';
    angular.bootstrap(document, [app['name']]);
});

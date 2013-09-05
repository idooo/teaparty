require.config({
    paths: {
        socketio: 'lib/socketio/socket.io',
        angular: 'lib/angular/angular',
        text: 'lib/require/text',

        // modules
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

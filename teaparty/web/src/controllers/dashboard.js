define([
    'momentjs'
], function() {
    return [
        '$scope', '$http', '$timeout', 'socket', 'progressbar',
        function($scope, $http, $timeout, socket, progressbar) {

        progressbar.start();

        var formatInstances = function(instances) {
            var running = [],
                not_running = [],
                result = {
                    running: 0,
                    total: 0,
                    statuses: []
                };

            if (typeof instances !== 'undefined') {
                result['running'] = instances['running'];
                result['total'] = instances['total'];


                instances['statuses'].forEach(function(status) {
                    if (status.state === 'running') {
                        running.push(status);
                    }
                    else {
                        not_running.push(status);
                    }
                });

                result['statuses'] = running.concat(not_running);
            }

            return result

        };

        var formatAlarms = function(alarms) {
            var s_ok = [],
                s_alarm = [],
                s_others = [],
                result = {
                    'count': 0,
                    'statuses': []
                };

            if (typeof alarms !== 'undefined') {
                result['count'] = alarms['count']

                alarms['statuses'].forEach(function(alarm) {
                    if (alarm.state === 'OK') {
                        s_ok.push(alarm);
                    }
                    else if (alarm.state === 'ALARM') {
                        s_alarm.push(alarm);
                    }
                    else {
                        s_others.push(alarm);
                    }
                });

                result['statuses'] = s_alarm.concat(s_ok, s_others);
            }

            return result
        };

        var getLastDate = function(metric_values, index) {
            var max_date = '';

            for (var key in metric_values) {
                if (metric_values.hasOwnProperty(key)) {
                    metric_values[key].forEach(function(value) {
                         if (max_date < value[index]) {
                             max_date = value[index];
                         }
                    });
                }
            }

            return moment.utc(max_date);
        };

        var startGlobalLoop = function(interval) {
            $scope.globalLoop = function() {
                $scope.cancelGlobalLoop = $timeout(function myFunction() {

                    console.log('After 10 secs');

                    $scope.cancelGlobalLoop = $timeout($scope.globalLoop, interval);
                }, interval);
            };

            $scope.globalLoop();
        };

        $scope.cancelGlobalLoop = function() {
            console.log($scope);
            $timeout.cancel($scope.cancelGlobalLoop);
        };

        $scope.blocks = [];

        // Request init data from server
        socket.emit('init');

        socket.on('response:init', function (data) {

            $scope.instances = formatInstances(data['instances']);
            $scope.alarms = formatAlarms(data['alarms'])

            $scope.blocks = data['structure'];
            $scope.metrics_values = data['metric_values'];

            // Store last metric date
            $scope.last_date = getLastDate($scope.metrics_values, 1);



            startGlobalLoop(1000);


            // Place init logic here

            progressbar.complete();

            // Start queue for getting data

        });

        socket.on('response:get_data', function (data) {
            console.log(data);
        });

        $scope.getData = function() {
            socket.emit('get_data', {'get': 'all'});
        };

        $scope.$apply();
    }];
});

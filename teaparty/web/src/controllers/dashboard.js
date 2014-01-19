define([
    'momentjs'
], function() {
    return [
        '$scope', '$http', '$timeout', 'socket', 'progressbar',
        function($scope, $http, $timeout, socket, progressbar) {

        progressbar.start();

        // Private ==========================================================

        var refresh_time = 60,
            global_loop_time = 10,
            _date_index = 1,
            _uid_index = 0,
            date_format = "YYYY-MM-DD hh:mm:ss";

        var formatData = function(value) {
            return {
                'y': value[2],
                'x': moment.utc(value[1], "YYYY-MM-DD hh:mm:ss").unix()
            }
        };

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

        var getLastDate = function(metric_values) {
            var max_date = '';

            for (var key in metric_values) {
                if (metric_values.hasOwnProperty(key)) {
                    metric_values[key].forEach(function(value) {
                         if (max_date < value[_date_index]) {
                             max_date = value[_date_index];
                         }
                    });
                }
            }

            if (!max_date) {
                return 0
            }
            else {
                return moment.utc(max_date, date_format);
            }

        };

        // Loop

        var globalLoop = function() {
            var current_time = moment.utc();

            if (current_time > $scope.next_date) {
                socket.emit('get_data', {
                    'date': $scope.next_date.format(date_format)
                });
                $scope.next_date = current_time.add('seconds', refresh_time);
            }
        };

        var startGlobalLoop = function(interval) {
            interval = interval * 1000;
            $scope.globalLoop = function() {
                $scope.loopTimer = $timeout(function myFunction() {
                    globalLoop();
                    $scope.loopTimer = $timeout($scope.globalLoop, interval);
                }, interval);
            };

            $scope.globalLoop();
        };

        var getData = function(data) {
            var max_date = '';

            if (!data.length) {
                return false;
            }

            data.forEach(function(value) {
                var graph_id = value[_uid_index].toString(),
                    graph = $scope.graphs[graph_id];

                $scope.metrics_values[graph_id].push(value);
                graph.series[0].data.push(formatData(value));

                if (max_date < value[_date_index]) {
                    max_date = value[_date_index]
                }

            });

            $scope.last_date = max_date;
        };

        // Mocks ============================================================

        window.get = function(graph_id) {
            var data = [
                [1, moment().format(date_format), Math.random()*100]
            ];

            var graph = $scope.graphs[graph_id.toString()];
            graph.series[0].data = []

            getData(data);
            graph.update();
        };


        // Public scope =====================================================

        $scope.cancelGlobalAppLoop = function() {
            $timeout.cancel($scope.loopTimer);
        };

        $scope.blocks = [];
        $scope.graphs = {};

        // Sockets ==========================================================

        /*
            Init logic
         */
        socket.on('response:init', function (data) {

            $scope.instances = formatInstances(data['instances']);
            $scope.alarms = formatAlarms(data['alarms']);

            $scope.blocks = data['structure'];
            $scope.metrics_values = data['metric_values'];

            // Store last metric date
            $scope.last_date = getLastDate($scope.metrics_values);
            $scope.next_date = $scope.last_date.add('seconds', refresh_time);

            startGlobalLoop(global_loop_time);

            progressbar.complete();

            // Start queue for getting data

        });

        /*
            Get data logic
         */
        socket.on('response:get_data', getData);

        socket.emit('init');

        $scope.$apply();
    }];
});


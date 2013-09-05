define([], function() {
    return ['$scope', '$http', 'socket', 'progressbar', function($scope, $http, socket, progressbar) {

        progressbar.start();

        var formatInstances = function(instances) {
            var running = [],
                not_running = [],
                result = {
                    running: instances['running'],
                    total: instances['total'],
                    statuses: []
                };

            instances['statuses'].forEach(function(status) {
                if (status.state === 'running') {
                    running.push(status);
                }
                else {
                    not_running.push(status);
                }
            });

            result['statuses'] = running.concat(not_running);
            return result

        };

        var formatAlarms = function(alarms) {
            var s_ok = [],
                s_alarm = [],
                s_others = [],
                result = {
                    'count': alarms['count']
                };

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
            return result
        };

        $scope.blocks = [];

        // Request init data from server
        socket.emit('init');

        socket.on('response:init', function (data) {

            $scope.instances = formatInstances(data['instances']);
            $scope.alarms = formatAlarms(data['alarms'])

            $scope.blocks = data['structure'];

            progressbar.complete();
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

define([], function() {
    return ['$scope', '$http', 'socket', function($scope, $http, socket) {

        $scope.blocks = []

        $http.get('/get_instances').success(function(data) {
            $scope.instances = data;
        });

        $http.get('/get_alarms').success(function(data) {
            $scope.alarms = data;
        });

        $http.get('/get_elb').success(function(data) {
            data.type = 'ELB';
            $scope.blocks.push(data);
        });

        socket.on('message', function (data) {
            console.log(data);
        });

        $scope.sendMessage = function() {
            socket.emit('say', {
                msg: 'pssst'
            })
        }

        $scope.$apply();
    }];
});
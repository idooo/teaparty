define([], function() {
    return ['$scope', '$http', 'socket', function($scope, $http, socket) {

        $scope.blocks = []

        // Request init data from server
        socket.emit('init')

        socket.on('response:init', function (data) {
            ['instances', 'alarms'].forEach(function(param){
                $scope[param] = data[param];
            });
            $scope.blocks = data['structure']
        });

        socket.on('response:get_data', function (data) {
            console.log(data);
        })

        $scope.getData = function() {
            socket.emit('get_data', {'get': 'all'});
        }

        $scope.$apply();
    }];
});

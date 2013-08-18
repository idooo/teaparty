define([], function() {
    return ['$scope', '$http', 'socket', function($scope, $http, socket) {

        $scope.blocks = []

        // Request init data from server
        socket.emit('init')

        socket.on('response:init', function (data) {
            _.each(['instances', 'alarms'], function(param){
                $scope[param] = data[param];
            });
            $scope.blocks.push(data['elb'])
        });

        $scope.$apply();
    }];
});
define([], function() {
    return ['$scope', '$http', function($scope, $http) {

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

        $scope.$apply();
    }];
});
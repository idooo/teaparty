define(['angular', 'src/services'], function (angular) {
	'use strict';

	return angular.module('teapartyApp.controllers', ['teapartyApp.services'])

		.controller('DashboardController', ['$scope', '$injector', function($scope, $injector) {
			require(['controllers/dashboard_ctrl'], function(dashctrl) {
				$injector.invoke(dashctrl, this, {'$scope': $scope});
			});
		}]);
});
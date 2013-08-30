define(['angular', 'src/services'], function(angular, services) {
	'use strict';

	angular.module('teapartyApp.directives', ['teapartyApp.services'])
		.directive('appVersion', ['version', function(version) {
			return function(scope, elm, attrs) {
				elm.text(version);
		};
	}]);
});
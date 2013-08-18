define(['angular', 'src/services'], function (angular, services) {
	'use strict';
	
	angular.module('teapartyApp.filters', ['teapartyApp.services'])
		.filter('interpolate', ['version', function(version) {
			return function(text) {
				return String(text).replace(/\%VERSION\%/mg, version);
			};
	}]);
});

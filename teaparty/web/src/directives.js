define(['angular', 'src/services'], function(angular, services) {
	'use strict';

	angular.module('teapartyApp.directives', ['teapartyApp.services'])
		.directive('appVersion', ['version', function(version) {
			return function(scope, elm, attrs) {
				elm.text(version);
		};
    }])
        .directive('minigraph', function() {
            return {
                restrict: 'A',
                scope: {
                    values:'=values',
                    min: '=min',
                    max: '=max'
                },
                template: '<div class="minigraph"></div>',
                replace: true,
                link: function postLink(scope, iElement, iAttrs) {

                    var data = [];
                    scope.values.forEach(function(value){
                        data.push(value[2]);
                    });

                    if (typeof scope.min === 'undefined') {
                        scope.min = d3.min(data)
                    }

                    if (typeof scope.max === 'undefined') {
                        scope.max = d3.max(data)
                    }

                    var w = 100, h = 40;
                    var yData = d3.scale.linear().domain([scope.min, scope.max]).range([0 , h]),
                        x = d3.scale.linear().domain([0, data.length]).range([0, w]);

                    var vis = d3.select(iElement[0])
                        .append("svg:svg")
                        .attr("width", w)
                        .attr("height", h);

                    var g = vis.append("svg:g")
                        .attr("transform", "translate(0, " + h     +")");

                    var lineData = d3.svg.line()
                        .x(function(d,i) { return x(i); })
                        .y(function(d) { return -1 * yData(d) });

                    g.append("svg:path").attr("d", lineData(data)).attr('class', 'data');

                }
        };
    });
});
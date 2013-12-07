define(['angular', 'src/services', 'momentjs'], function(angular, services) {
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
                    values:'=',
                    min: '=',
                    max: '='
                },
                transclude: false,
                template: '<div class="minigraph"></div>',
                replace: true,
                link: function(scope, iElement, iAttrs) {

                    var width = 150,
                        height = 40;

                    var data = [];
                    var i = 0;
                    scope.values.forEach(function(value){
                        data.push({
                            'y': value[2],
                            'x': moment.utc(value[1], "YYYY-MM-DD hh:mm:ss").unix()
                        });
                    });

                    if (typeof scope.min === 'undefined') {
                        scope.min = d3.min(data)
                    }

                    if (typeof scope.max === 'undefined') {
                        scope.max = d3.max(data)
                    }

                    // ===========================================

                    var graph = new Rickshaw.Graph( {
                        element: iElement[0],
                        width: width,
                        height: height,
                        max: scope.max,
                        min: scope.min,
                        onData: function(d) {  d[0].data[0].y = 80; return d; },
                        series: [{
                            color: 'steelblue',
                            data: data
                        }]
                    });

                    var hoverDetail = new Rickshaw.Graph.HoverDetail( {
                        graph: graph,
                        yFormatter: function(y) { return Math.round(y * 100) / 100 + " %" }
                    } );

                    graph.render();

                    scope.$watch('values',      function() {console.log('pew') });

                }
        };
    });
});
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
                    max: '=',
                    graphs: '=',
                    uid: '='
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

                    console.log(data);

                    window.__.deadSimpleGraph(iElement[0], data, {
                        'width': 100,
                        'height': 50,
                        'point_radius': 1
                    });

                    setInterval(function(){
                        if (Math.random() > 0.3) {
                            var x = new Date().getTime(),
                                y = Math.random()* Math.random()*100;

                            iElement[0].graph.addPoint({'x': x, 'y': y});
                        }

                        iElement[0].graph.update();
                    }, 1000);

                    // scope.graphs['' + scope.uid] = graph;

                }
        };
    });
});
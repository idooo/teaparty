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
                    values:'=values',
                    min: '=min',
                    max: '=max'
                },
                template: '<div class="minigraph"></div>',
                replace: true,
                link: function postLink(scope, iElement, iAttrs) {

                    var data = [];
                    scope.values.forEach(function(value){
                        data.push({
                            'value': value[2],
                            'date': moment.utc(value[1], "YYYY-MM-DD hh:mm:ss").toDate()
                        });
                    });

                    console.log(data);

                    if (typeof scope.min === 'undefined') {
                        scope.min = d3.min(data)
                    }

                    if (typeof scope.max === 'undefined') {
                        scope.max = d3.max(data)
                    }

                    // ===========================================

                    var margin = {top: 20, right: 50, bottom: 20, left: 20},
                        width = 150,
                        height = 40;

                    var bisectDate = d3.bisector(function(d) { return d.date; }).left,
                        formatValue = d3.format(",.2f");

                    var x = d3.time.scale()
                        .range([0, width]);

                    var y = d3.scale.linear()
                        .range([height, 0]);

                    var xAxis = d3.svg.axis()
                        .scale(x)
                        .orient("bottom");

                    var yAxis = d3.svg.axis()
                        .scale(y)
                        .orient("left");

                    var line = d3.svg.line()
                        .x(function(d) { return x(d.date); })
                        .y(function(d) { return y(d.value); });

                    var svg = d3.select(iElement[0]).append("svg")
                        .attr("width", width)
                        .attr("height", height + margin.top + margin.bottom)
                        .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                    x.domain([data[0].date, data[data.length - 1].date]);
                    y.domain(d3.extent(data, function(d) { return d.value; }));

                    svg.append("path")
                        .datum(data)
                        .attr("class", "line")
                        .attr("d", line);

                    var focus = svg.append("g")
                        .attr("class", "focus")
                        .style("fill", 'red');

                    focus.append("circle")
                        .attr("r", 2);

                    focus.append("text")
                        .attr("x", 9)
                        .attr("dy", ".35em");

                    svg.append("rect")
                        .attr("class", "overlay")
                        .attr("width", width)
                        .attr("height", height)
                        .on("mouseover", function() { focus.style("display", null); })
                        .on("mouseout", function() { focus.style("display", "none"); })
                        .on("mousemove", mousemove);

                    function mousemove() {
                        var x0 = x.invert(d3.mouse(this)[0]),
                            i = bisectDate(data, x0, 1),
                            d0 = data[i - 1],
                            d1 = data[i],
                            d = x0 - d0.date > d1.date - x0 ? d1 : d0;
                        focus.attr("transform", "translate(" + x(d.date) + "," + y(d.value) + ")");
                        focus.select("text").text(formatValue(d.value));
                    }

                }
        };
    });
});
/**
 * Dead simple graph lib to display real-time last updated data
 *
 * Options:
 * =====================================================================================================================
 * width (int) - vertical size of graph
 * height (int) - horizontal size of graph
 * show_points (bool) - display or not data points or only display lines
 * point_radius (int) - radius of data points
 * minutes (int) - amount of the last minutes of data to display
 * threshold (int) - min value for Y to start warning about
 * max_value (int) - max possible value for Y
 * color (string) - default color for elements
 * warning_color - warning color for elements
 *
 */

(function(window) {
    'use strict';

    var DeadSimpleGraph = function(element, data, options) {
        this.container = element;
        this.options = {};

        this.options.width = options.width || 300;
        this.options.height = options.height || 100;
        this.options.point_radius = options.point_radius || 2;
        this.options.minutes = options.minutes || 1;
        this.options.threshold = options.threshold || 50;
        this.options.show_points = options.show_points || false;
        this.options.g_max_y_value = options.max_value || 100;

        this.options.color = options.color || 'green';
        this.options.warning_color = options.warning_color || 'red';

        this.svgns = "http://www.w3.org/2000/svg";
        this.svg_body = document.createElementNS(this.svgns, "svg");

        this.data = data;
        this.data_added = 0;

        this.g_max_y = options.height;
        this.g_max_x = options.width;

        this.g_min_time = this.options.minutes * 60 * 1000 // 1 minute

        this._classname = 'dsg-container';

        this.init();
    };

    DeadSimpleGraph.prototype = {

        constructor: DeadSimpleGraph,

        init: function () {
            console.log('init here');
            this.container.appendChild(this.svg_body);
            this._drawData();

            // styling
            this.container.className += ' ' + this._classname;
            this.container.style.width = this.options.width + 'px';
            this.container.style.height = this.options.height + 'px';
        },

        _drawData: function() {
            var data = this._dataTransition(this.data),
                point_color = this.options.color,
                line_color = this.options.color;

            // check threshold
            if (data.length > 0 && data[data.length - 1].y >= this.options.threshold) {
                line_color = this.options.warning_color;
            }

            // initial draw
            for (var i = 0; i < data.length; i++ ) {
                var d = data[i];
                if (this.options.show_points) {
                    if (i + 1 === data.length) {
                        point_color = this.options.warning_color;
                    }
                    this._drawPoint(d.x, d.y, this.options.point_radius, point_color);
                }
                if (i !== 0) {
                    var p = data[i-1];
                    this._drawLine(p.x, p.y, d.x, d.y, line_color);
                }
            }
        },

        _dataTransition: function(raw_data) {
            var current_time = new Date().getTime(),
                min = current_time - this.g_min_time,
                scale_x = this.g_min_time / this.g_max_x,
                scale_y = this.g_max_y / this.options.g_max_y_value,
                data = [];

            for (var i = 0; i < raw_data.length; i++) {
                if (raw_data[i].x >= min && raw_data[i].x < current_time) {
                    var x = (raw_data[i].x - min) / scale_x,
                        y = this.g_max_y - (raw_data[i].y * scale_y);

                    data.push({
                        'x': x,
                        'y': y
                    });
                }
            }
            return data;
        },

        _shape: function(name) {
            return document.createElementNS(this.svgns, name);
        },

        _paint: function(shape) {
            this.svg_body.appendChild(shape);
        },

        _clear: function() {
            while (this.svg_body.firstChild) {
                this.svg_body.removeChild(this.svg_body.firstChild);
            }
        },

        _drawPoint: function(x, y, radius, color) {
            radius = radius || this.options.point_radius;
            color = color || this.options.color;

            var shape = this._shape("circle");
            shape.setAttributeNS(null, "cx", x);
            shape.setAttributeNS(null, "cy", y);
            shape.setAttributeNS(null, "r",  radius);
            shape.setAttributeNS(null, "fill", color);

            this._paint(shape);
        },

        _drawLine: function(x1, y1, x2, y2, color) {
            color = color || this.options.color;

            var shape = this._shape("line");
            shape.setAttributeNS(null, "x1", x1);
            shape.setAttributeNS(null, "y1", y1);
            shape.setAttributeNS(null, "x2", x2);
            shape.setAttributeNS(null, "y2", y2);
            shape.setAttributeNS(null, "stroke", color);

            this._paint(shape);
        },

        addPoint: function(data) {
            this.data.push(data);
            this.data_added++;
        },

        update: function() {
            this._clear();
            this._drawData();
            this.data_added = 0;
        }
    };

    if (typeof window.__ === 'undefined') { window.__ = {}; }

    window.__.deadSimpleGraph = function(element, data, options) {
        element.graph = new DeadSimpleGraph(element, data, options);
    }

})(window);

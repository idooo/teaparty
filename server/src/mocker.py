
class ResponseMocker():

	def getInstances(self):

		return {
			'running': 11,
			'total': 30,
		    'statuses': [
			    {'id': 'i-0000001', 'status': 1},
			    {'id': 'i-0000002', 'status': 2},
			    {'id': 'i-0000003', 'status': 1},
			    {'id': 'i-0000004', 'status': 3}
		    ]
		}

	def getAlarms(self):

		return {
			'count': 32,
		    'statuses': [
			    {'code': 'a-0000001', 'status': 1},
			    {'code': 'a-0000002', 'status': 1},
			    {'code': 'a-0000003', 'status': 3},
			    {'code': 'a-0000004', 'status': 1},
			    {'code': 'a-0000005', 'status': 2},
			    {'code': 'a-0000006', 'status': 3},
		    ]
		}

	def getELB(self):

		return {
			'name': 'prod-web',
		    'metrics': [
			    {'name': 'MetricRequests', 'caption': 'requests', 'units': '', 'value': 421, 'time': 12412412},
			    {'name': 'MetricLatency', 'caption': 'latency', 'units': 'ms', 'value': 100, 'time': 12412412}
			],
		    'instances': [
			    {
				    'name': 'Prod-WEB-Alpha',
			        'id': 'i-0000001',
			        'metrics': [
				        {'name': 'MetricCPU', 'caption': 'cpu', 'units': '%', 'value': 40, 'time': 12412412},
				        {'name': 'MetricMemory', 'caption': 'memory', 'units': '%', 'value': 14, 'time': 12412412},
				        {'name': 'MetricHDDSpace', 'caption': 'disk space', 'units': '%', 'value': 7, 'time': 12412412},
			        ]
			    },
			    {
			    'name': 'Prod-WEB-Beta',
			    'id': 'i-0000002',
			    'metrics': [
					    {'name': 'MetricCPU', 'caption': 'cpu', 'units': '%', 'value': 42, 'time': 12412412},
					    {'name': 'MetricMemory', 'caption': 'memory', 'units': '%', 'value': 19, 'time': 12412412},
					    {'name': 'MetricHDDSpace', 'caption': 'disk space', 'units': '%', 'value': 11, 'time': 12412412},
				    ]
			    }
		    ]
		}


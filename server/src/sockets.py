from socketio.namespace import BaseNamespace
from mocker import ResponseMocker

class TeapartyNamespace(BaseNamespace):
	sockets = {}
	server = ResponseMocker()

	def recv_connect(self):
		print "Got a socket connection" # debug
		self.sockets[id(self)] = self

	def disconnect(self, *args, **kwargs):
		print "Got a socket disconnection" # debug
		if id(self) in self.sockets:
			del self.sockets[id(self)]
		super(TeapartyNamespace, self).disconnect(*args, **kwargs)

	def response(self, event, message):
		socket_id = id(self)

		if socket_id in self.sockets.keys():
			self.sockets[socket_id].emit(event, message)

	def on_init(self, message):
		data = {
			'instances': self.server.getInstances(),
			'alarms': self.server.getAlarms(),
			'elb': self.server.getELB()
		}

		self.response('response:init', data)

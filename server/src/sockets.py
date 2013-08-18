from socketio.namespace import BaseNamespace

class TeapartyNamespace(BaseNamespace):
	sockets = {}

	def recv_connect(self):
		print "Got a socket connection" # debug
		self.sockets[id(self)] = self

	def disconnect(self, *args, **kwargs):
		print "Got a socket disconnection" # debug
		if id(self) in self.sockets:
			del self.sockets[id(self)]
		super(TeapartyNamespace, self).disconnect(*args, **kwargs)

	def response(self, socket_id, event, message):
		if socket_id in self.sockets.keys():
			self.sockets[socket_id].emit(event, message)

	def on_say(self, message):
		print message
		self.response(id(self), 'message', 'got it')
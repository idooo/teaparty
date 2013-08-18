
import src as library
from src.sockets import TeapartyNamespace
from flask import Flask, render_template, Response, request, jsonify

import werkzeug.serving
from gevent import monkey
from socketio import socketio_manage
from socketio.server import SocketIOServer

SOCKET_URL = '/socket'

app = Flask(
	__name__,
	static_folder='../app',
	static_url_path='',
	template_folder='../app'
)
monkey.patch_all()

response = library.ResponseMocker()

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/get_instances")
def get_instances():
	return jsonify(response.getInstances())

@app.route("/get_alarms")
def get_alarms():
	return jsonify(response.getAlarms())

@app.route("/get_elb")
def get_elb():
	return jsonify(response.getELB())

@app.route('/socket.io/<path:rest>')
def push_stream(rest):
	try:
		socketio_manage(request.environ, {SOCKET_URL: TeapartyNamespace}, request)
	except:
		app.logger.error("Exception while handling socketio connection", exc_info=True)
	return Response()

@werkzeug.serving.run_with_reloader
def run_dev_server():
	app.debug = True
	port = 5000
	SocketIOServer(('', port), app, resource="socket.io").serve_forever()

if __name__ == "__main__":
	run_dev_server()
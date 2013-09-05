
import __main__
from teaparty.sockets import TeapartyNamespace
from flask import Flask, render_template, Response, request, jsonify

import werkzeug.serving
from gevent import monkey
from socketio import socketio_manage
from socketio.server import SocketIOServer

params = __main__.params

app = Flask(
    __name__,
    static_folder=params['root'],
    static_url_path='',
    template_folder=params['root']
)
monkey.patch_all()

@app.route("/")
def main():
    return render_template('index.html')


@app.route('/socket.io/<path:rest>')
def push_stream(rest):
    try:
        socketio_manage(request.environ, {params['socket_url']: TeapartyNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection", exc_info=True)
    return Response()

@werkzeug.serving.run_with_reloader
def run_dev_server():
    app.debug = params['debug']
    SocketIOServer(('', params['port']), app, resource="socket.io").serve_forever()

run_dev_server()
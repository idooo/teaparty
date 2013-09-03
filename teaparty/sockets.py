from socketio.namespace import BaseNamespace
from teaparty.model import DBAdapter, CloudWatchHelper, EC2Helper

try:
    from __main__ import REGION
except ImportError:
    REGION = None

class TeapartyNamespace(BaseNamespace):
    sockets = {}

    region = REGION

    db = DBAdapter()
    cw = CloudWatchHelper(region)
    ec2 = EC2Helper(region)

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
            'instances': self.ec2.getInstances(),
            'alarms': self.cw.getAlarms(),
            'structure': self.db.reflectStructure()
        }

        self.response('response:init', data)

    def on_get_data(self, message):
        if not 'get' in message:
            return False

        metric_uid = None
        if not message['get'] in ['all']:
            metric_uid = message['get']

        cursor = self.db.connection.cursor()

        date = None
        if 'time' in message:
            date = message['time']

        results = self.db.getMetricValues(metric_uid=metric_uid, date=date, cursor=cursor)
        self.response('response:get_data', results)

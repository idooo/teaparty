from socketio.namespace import BaseNamespace
from teaparty import DBAdapter, CloudWatchHelper, EC2Helper
import __main__

class TeapartyNamespace(BaseNamespace):
    sockets = {}

    def initialize(self):
        region = __main__.params['region']
        self.db = DBAdapter()
        self.cw = CloudWatchHelper(region)
        self.ec2 = EC2Helper(region)

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

            # TODO: Cache this data:

            'instances': self.ec2.getInstances(),
            'alarms': self.cw.getAlarms(),
            'structure': self.db.reflectStructure(),
            'metric_values': self.db.getAllMetricValues()
        }

        self.response('response:init', data)

    def on_get_data(self, message):
        count = 100
        date = None
        metric_uid = None

        cursor = self.db.connection.cursor()

        if 'count' in message:
            count = int(message['count'])

        if 'date' in message:
            date = message['date']

        if 'metric_uid' in message:
            metric_uid = message['metric_uid']

        results = self.db.getMetricValues(
            metric_uid=metric_uid,
            date=date,
            sort='date',
            limit=count,
            cursor=cursor
        )

        self.response('response:get_data', results)

#!/usr/bin/python

from src import CloudWatchHelper, ELBHelper, DBAdapter, Executor

# TODO: Move to separate config
config = [
    {
        'type': 'elb',
        'name': 'prod-web',
        'metrics': ['Latency|Seconds', 'RequestCount|Count'],
        'child_metrics': ['CPUUtilization', 'UsedMemoryPercent', 'UsedSpacePercent||Path:/data', 'test||path:/data,year:2010']
    }
]

class MetricDaemon():

    cw = None
    elb = None
    db = None

    # TODO: Move to config
    dbname = 'db/test.db'

    queue = []

    def __init__(self, config=None, dbname='db/test.db'):
        self.cw = CloudWatchHelper('ap-southeast-2')
        self.elb = ELBHelper('ap-southeast-2')

        self.db = DBAdapter(dbname)
        self.dbname = dbname

        if config:
            self.__parseConfig(config)

        self.__createQueue()

    def __parseConfig(self, config):

        elbs = self.elb.getLoadBalancers()

        # TODO: Error handling
        for obj in config:

            # Load balancer logic
            if obj['type'] == 'elb':

                if not obj['name'] in elbs:
                    raise Exception('There is not ELB with name ' + obj['name'])

                obj['instances'] = elbs[obj['name']].instances[:]

                elb_uid = self.db.addELB(obj['name'], obj['metrics'])
                instances_uids = []

                for instance in obj['instances']:
                    instances_uids.append(self.db.addInstance(instance.id, obj['child_metrics']))

                self.db.addGroup(elb_uid, instances_uids)

    def __addToQueue(self, obj_type, obj_code, metric):

        dimensions = metric['dimensions']

        if obj_type == 'elb':
            dimensions.update({'LoadBalancerName': obj_code})

        elif obj_type == 'instance':
            dimensions.update({'InstanceId': obj_code})

        else:
            raise Exception('Unknown object type ' + str(obj_type))

        item = {
            'name': metric['name'],
            'uid': metric['uid'],
            'dimensions': dimensions,
            'namespace': metric['namespace'],
            'unit': metric['unit']
        }

        self.queue.append(item.copy())

    def __getNamespaces(self, dimensions):
        metrics = self.cw.getMetrics(dimensions=dimensions)
        namespaces = {}
        for metric in metrics:
            namespaces.update({str(metric.name): metric.namespace})

        return namespaces

    def __addNamespace(self, metric, namespaces):
        if metric['name'] in namespaces:
            metric['namespace'] = namespaces[metric['name']]
            return metric

        return False

    def __createQueue(self):

        self.queue = []

        metrics = self.db.getMetrics()
        instances = self.db.getInstances()
        elbs = self.db.getELBs()

        for elb_uid in elbs:
            elb_name = elbs[elb_uid]['name']
            namespaces = self.__getNamespaces({'LoadBalancerName': elb_name})

            for metric_uid in elbs[elb_uid]['metrics']:
                metric = self.__addNamespace(metrics[str(metric_uid)], namespaces)
                if metric:
                    self.__addToQueue('elb', elb_name, metric)

        for instance_uid in instances:
            namespaces = self.__getNamespaces({'InstanceId': instances[instance_uid]['id']})
            for metric_uid in instances[instance_uid]['metrics']:
                metric = self.__addNamespace(metrics[str(metric_uid)], namespaces)
                if metric:
                    self.__addToQueue('instance', instances[instance_uid]['id'], metric)

    def start(self, debug=False):
        if not self.queue:
            print 'Queue is empty. Please load config first'
            return False

        e = Executor(self.cw.getMetricData, self.queue, self.dbname, latency=2, debug=debug)
        e.execute(4)

if __name__ == '__main__':
    coyote = MetricDaemon(config)
    coyote.start(debug=False)

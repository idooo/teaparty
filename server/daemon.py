#!/usr/bin/python

from src import CloudWatchHelper, ELBHelper, DBAdapter

config = [
    {
        'type': 'elb',
        'name': 'prod-web',
        'metrics': ['Latency', 'RequestCount'],
        'child_metrics': ['CPUUtilization', 'UsedMemoryPercent', 'UsedSpacePercent|Path:/data', 'test|path:/data,year:2010']
    }
]

class MetricDaemon():

    cw = None
    elb = None
    db = None

    queue = []

    def __init__(self, config=None):
        self.cw = CloudWatchHelper('ap-southeast-2')
        self.elb = ELBHelper('ap-southeast-2')

        self.db = DBAdapter('db/test.db')

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
            'dimensions': dimensions
        }

        self.queue.append(item.copy())

    def __createQueue(self):

        self.queue = []

        metrics = self.db.getMetrics()
        instances = self.db.getInstances()
        elbs = self.db.getELBs()

        for elb_uid in elbs:
            for metric_uid in elbs[elb_uid]['metrics']:
                self.__addToQueue('elb', elbs[elb_uid]['name'], metrics[str(metric_uid)])

        for instance_uid in instances:
            for metric_uid in instances[instance_uid]['metrics']:
                self.__addToQueue('instance', instances[instance_uid]['id'], metrics[str(metric_uid)])

if __name__ == '__main__':
    coyote = MetricDaemon(config)



# metrics = cw.getMetrics('CPUUtilization', dimensions={'InstanceId': 'i-11d5d62c'})

# a = cw.getMetricData(metrics[0])

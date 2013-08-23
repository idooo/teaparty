#!/usr/bin/python

from src import CloudWatchHelper, ELBHelper, DBAdapter

config = [
    {
        'type': 'elb',
        'name': 'prod-web',
        'metrics': ['Latency', 'RequestCount'],
        'child_metrics': ['CPUUtilization', 'UsedMemoryPercent', 'UsedSpacePercent|Path:/data']
    }
]

class MetricDaemon():

    cw = None
    elb = None

    def __init__(self, config):
        self.cw = CloudWatchHelper('ap-southeast-2')
        self.elb = ELBHelper('ap-southeast-2')

        self.db = DBAdapter('db/test.db')

        self.__parseConfig(config)

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

if __name__ == '__main__':
    coyote = MetricDaemon(config)



# metrics = cw.getMetrics('CPUUtilization', dimensions={'InstanceId': 'i-11d5d62c'})

# a = cw.getMetricData(metrics[0])

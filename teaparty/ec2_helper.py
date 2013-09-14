import boto.ec2
from helpers import cache

class EC2Helper():

    conn = False

    # state codes
    RUNNING = 16
    PENDING = 0
    STOPPING = 64
    TERMINATED = 48
    STOPPED = 80

    def __init__(self, region):
        self.connect(region)

    def connect(self, region):
        """
        Create AWS EC2 connection

        :type region: string
        :param region: Region to connect
        """

        self.conn = boto.ec2.connect_to_region(region)

        if not self.conn:
            raise Exception('Invalid region name')
            return False

    @cache
    def getInstances(self):
        _raw = self.conn.get_only_instances()
        result = {
            'running': 0,
            'total': 0,
            'statuses': []
        }

        if _raw:
            instances = []
            for instance in _raw:
                if instance.state_code == self.RUNNING:
                    result['running'] += 1

                instances.append({
                    'id': instance.id,
                    'state_code': instance.state_code,
                    'state': instance.state
                })

            result['total'] = len(instances)
            result['statuses'] = instances

        return result

if __name__ == '__main__':
    c = EC2Helper('ap-southeast-2')
    print c.getInstances()
    print c.getInstances()
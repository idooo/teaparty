

class metricQueue(list):
    """
    Class to store tasks. Workers get task data from queue
    by reading data by cursor and moving this cursor after each read
    """
    cursor = 0
    body = []

    ended = False

    def add(self, obj_type, obj_code, metric):
        """ 
        Add list of items to queue
        """

        if not metric:
            return False

        dimensions = metric['dimensions']

        if obj_type == 'elb':
            dimensions.update({'LoadBalancerName': obj_code})

        elif obj_type == 'instance':
            dimensions.update({'InstanceId': obj_code})

        else:
            raise NameError('Unknown object type ' + str(obj_type))

        item = {
            'name': metric['name'],
            'uid': metric['uid'],
            'dimensions': dimensions,
            'namespace': metric['namespace'],
            'unit': metric['unit']
        }

        self.body.append(item.copy())

        return True

    def isEmpty(self):
        return not bool(self.body)

    def next(self):
        """
        Move cursor to next position. Mark queue as ended 
        if cursor was moved to the last position of queue
        """
        self.cursor += 1
        if self.cursor == len(self.body):
            self.cursor = 0
            self.ended = True

    def get(self):
        """
        Read element from queue and move cursor to the next position

        :rtype: :object
        :returns: Queue item
        """
        result = self.body[self.cursor]
        self.next()
        return result

    def renew(self):
        """ Renew queue to mark it as not ended"""
        self.ended = False


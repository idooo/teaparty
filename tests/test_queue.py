import sys
sys.path.append('../')

import unittest
from teaparty import metricQueue


class metricQueueCase(unittest.TestCase):

    def setUp(self):
        self.queue = metricQueue()

    def test_add(self):

        tests = [
            {'type': 'elb', 'code': 'elb1', 'metric': {'uid': 1, 'name': 'metric1', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'lala': 111}}},
            {'type': 'elb', 'code': 'elb2', 'metric': {'uid': 2, 'name': 'metric2', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'opop': 222}}},
            {'type': 'instance', 'code': 'instance1', 'metric': {'uid': 3, 'name': 'metric3', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'dada': 333}}},
            {'type': 'instance', 'code': 'instance2', 'metric': {'uid': 4, 'name': 'metric4', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {}}}
        ]

        for test in tests:
            self.queue.add(test['type'], test['code'], test['metric'])

        ex =  {'type': 'block', 'code': 'elb2', 'metric': {'uid': 2, 'name': 'metric2', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'opop': 222}}}

        with self.assertRaises(NameError):
            self.queue.add(ex['type'], ex['code'], ex['metric'])

        for i in range(0, len(tests)):
            item = self.queue.body[i]
            self.assertTrue(item['uid'], tests[i]['metric']['uid'])
            self.assertTrue(item['name'], tests[i]['metric']['name'])

    def test_isEmpty(self):
        pass

    def test_next(self):
        pass

    def test_get(self):
        pass

    def test_renew(self):
        pass

if __name__ == '__main__':
    unittest.main()

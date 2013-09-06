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
            self.assertEqual(item['uid'], tests[i]['metric']['uid'])
            self.assertEqual(item['name'], tests[i]['metric']['name'])

    def test_isEmpty(self):
        self.queue = metricQueue()
        self.assertTrue(self.queue.isEmpty())

        ex =  {'type': 'block', 'code': 'elb2', 'metric': {'uid': 2, 'name': 'metric2', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'opop': 222}}}
        with self.assertRaises(NameError):
            self.queue.add(ex['type'], ex['code'], ex['metric'])

        self.assertTrue(self.queue.isEmpty())

        item = {'type': 'elb', 'code': 'elb1', 'metric': {'uid': 1, 'name': 'metric1', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'lala': 111}}}
        self.queue.add(item['type'], item['code'], item['metric'])

        self.assertFalse(self.queue.isEmpty())

    def test_get_next(self):
        tests = [
            {'type': 'instance', 'code': 't1', 'metric': {'uid': 1, 'name': 'metric1', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'lala': 111}}},
            {'type': 'instance', 'code': 't2', 'metric': {'uid': 2, 'name': 'metric2', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'opop': 222}}},
            {'type': 'instance', 'code': 't3', 'metric': {'uid': 3, 'name': 'metric3', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'dada': 333}}},
            {'type': 'instance', 'code': 't4', 'metric': {'uid': 4, 'name': 'metric4', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {}}}
        ]

        for test in tests:
            self.queue.add(test['type'], test['code'], test['metric'])

        count = 0
        for test in tests:
            self.assertEqual(count, self.queue.cursor)
            count += 1

            item = self.queue.get()
            self.assertEqual(test['metric']['uid'], item['uid'])

        self.assertTrue(self.queue.ended)
        self.assertEqual(self.queue.cursor, 0)

    def test_renew(self):
        tests = [
            {'type': 'instance', 'code': 't1', 'metric': {'uid': 1, 'name': 'metric1', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'lala': 111}}},
            {'type': 'instance', 'code': 't2', 'metric': {'uid': 2, 'name': 'metric2', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'opop': 222}}},
            {'type': 'instance', 'code': 't3', 'metric': {'uid': 3, 'name': 'metric3', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {'dada': 333}}},
            {'type': 'instance', 'code': 't4', 'metric': {'uid': 4, 'name': 'metric4', 'namespace': 'EC', 'unit': 'Percent', 'dimensions': {}}}
        ]

        for test in tests:
            self.queue.add(test['type'], test['code'], test['metric'])

        self.assertFalse(self.queue.ended)

        for test in tests:
            self.queue.get()

        self.assertTrue(self.queue.ended)

        self.queue.renew()
        self.assertFalse(self.queue.ended)

if __name__ == '__main__':
    unittest.main()

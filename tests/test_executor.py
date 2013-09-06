__author__ = 'ashteinikov'

import sys
from time import sleep
sys.path.append('../')

import unittest
import datetime

from teaparty import executor, metricQueue
from mock import Mock

class ExecutorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.dates = {
            'n1': datetime.datetime(2013, 1, 1, 1, 1, 1, 1),
            'n12': datetime.datetime(2013, 1, 1, 1, 2, 1, 1),

            'n2': datetime.datetime(2114, 2, 1, 1, 1, 1, 1),
            'n3': datetime.datetime(2013, 3, 1, 1, 1, 1, 1),
            'n4': datetime.datetime(2013, 4, 1, 1, 1, 1, 1),
            'n42': datetime.datetime(2013, 4, 1, 1, 2, 1, 1),
            'n43': datetime.datetime(2114, 4, 1, 1, 3, 1, 1),

            'n5': datetime.datetime(2013, 5, 1, 1, 1, 1, 1),
            'n6': datetime.datetime(2114, 6, 1, 1, 1, 1, 1),
        }

        self.values = {
            'n1': 1.51251, 'n12': 12.98761,
            'n2': 2.251,
            'n3': 3.51,
            'n4': 4.21, 'n42': 42.15171, 'n43': 43.167167,
            'n5': 5.0002,
            'n6': 6.241
        }

        def mocker(name, namespace, dimensions, unit):
            time = self.dates[namespace]
            result = [{'Timestamp': time, 'value': self.values[namespace]}]
            if namespace == 'n1':
                result.append({'Timestamp': time, 'value': self.values[namespace+'2']})

            elif namespace == 'n4':
                result.append({'Timestamp': time, 'value': self.values[namespace+'2']})
                result.append({'Timestamp': time, 'value': self.values[namespace+'3']})

            return result

        tests = [
            {'type': 'instance', 'code': 't1', 'metric': {'uid': 1, 'name': 'metric1', 'namespace': 'n1', 'unit': 'Percent', 'dimensions': {'lala': 111}}},
            {'type': 'instance', 'code': 't2', 'metric': {'uid': 2, 'name': 'metric1', 'namespace': 'n2', 'unit': 'Percent', 'dimensions': {'lala': 1111}}},
            {'type': 'instance', 'code': 't3', 'metric': {'uid': 3, 'name': 'metric2', 'namespace': 'n3', 'unit': 'Percent', 'dimensions': {'opop': 222}}},
            {'type': 'instance', 'code': 't4', 'metric': {'uid': 4, 'name': 'metric3', 'namespace': 'n4', 'unit': 'Percent', 'dimensions': {'dada': 333}}},
            {'type': 'instance', 'code': 't2', 'metric': {'uid': 2, 'name': 'metric4', 'namespace': 'n5', 'unit': 'Percent', 'dimensions': {}}},
            {'type': 'instance', 'code': 't1', 'metric': {'uid': 1, 'name': 'metric4', 'namespace': 'n6', 'unit': 'Percent', 'dimensions': {}}}
        ]

        queue = metricQueue()

        for test in tests:
            queue.add(test['type'], test['code'], test['metric'])

        self.e = executor.Executor(mocker, queue, debug=True, dbname=':memory:')

    def test_execute(self):
        self.e.debug_dry_run = True
        self.e.execute(1)
        sleep(1)

        self.assertEqual(len(self.e.result_pool), 6)

        items = self.e.result_pool

        self.assertEqual(items[0]['1'][0]['Timestamp'], self.dates['n1'])
        self.assertEqual(items[2]['3'][0]['Timestamp'], self.dates['n3'])
        self.assertEqual(items[3]['4'][0]['Timestamp'], self.dates['n4'])

        self.assertEqual(items[2]['3'][0]['value'], self.values['n3'])
        self.assertEqual(items[3]['4'][1]['value'], self.values['n42'])
        self.assertEqual(items[3]['4'][2]['value'], self.values['n43'])

    def test_saveDataFromPool(self):

        #print self.e.result_pool

        self.e.saveDataFromPool()

        metrics = self.e.db.getMetricValues(1)
        self.assertEqual(metrics[0][2], self.values['n1'])
        self.assertEqual(metrics[1][2], self.values['n12'])
        self.assertEqual(metrics[2][2], self.values['n6'])

        metrics = self.e.db.getMetricValues(4)

        self.assertEqual(metrics[0][2], self.values['n4'])
        self.assertEqual(metrics[1][2], self.values['n42'])
        self.assertEqual(metrics[2][2], self.values['n43'])

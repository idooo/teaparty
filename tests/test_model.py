__author__ = 'ido'

import sys
sys.path.append('../')

import unittest
from sqlite3 import OperationalError

from teaparty import model, ELBHelper
from mock import Mock

from conf import config

class _ELBs():
    def __init__(self, data):
        self.instances = data[:]

class _EC():
    def __init__(self, _id):
        self.id = _id

class ModelTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.model = model.DBAdapter(':memory:')

        data = {
            'groups': [
                [1, '', 1, '1|2']
            ],
            'elbs': [
                [1, 'test', '1|2']
            ],
            'instances': [
                [1, 'i-0001', '3|4'],
                [2, 'i-0003', '5|6']
            ],
            'metrics': [
                [1,"Latency", "", "Seconds" ],
                [2,"RequestCount",  "", "Count" ],
                [3,"pewpewpew", "", "Percent" ],
                [4,"UsedMemoryPercent", "", "Percent" ],
                [5,"UsedSpacePercent", "Path:/data", "Hours" ],
                [6,"test", "path:/data,year:2010", "Percent" ]
            ],
            'metric_values': [

            ]
        }

        c = self.model.connection.cursor()
        for table_name in data:
            for row in data[table_name]:
                params = []
                for value in row:
                    if isinstance(value, str):
                        params.append('"' + value + '"')
                    else:
                        params.append(str(value))

                query = 'INSERT INTO ' + table_name + ' VALUES(' + ','.join(params) + ')'
                c.execute(query)

        # recalculate counters
        self.model.getCounters()

        self.model.connection.commit()

    def __get(self, table_name, uid):
        c = self.model.connection.cursor()
        c.execute('SELECT * FROM {0} WHERE uid={1}'.format(table_name, uid))
        return c.fetchone()

    def test__initTables(self):
        c = self.model.connection.cursor()

        for table in self.model.format:
            c.execute("SELECT * FROM " + table['name'])

        self.assertEqual(True, True)

    def test__uid(self):
        prev = self.model.counters['elbs']
        self.model._DBAdapter__uid('elbs')
        self.assertEqual(prev+1, self.model.counters['elbs'])

    def test__isExist(self):
        a1 = self.model._DBAdapter__isExist('instances', 'uid=1')
        a2 = self.model._DBAdapter__isExist('instances', 'uid=9999')

        try:
            a3 = self.model._DBAdapter__isExist('null', 'uid=1')
        except OperationalError:
            a3 = 'nice'

        self.assertTrue(a1)
        self.assertFalse(a2)
        self.assertEqual(a3, 'nice')

    def test__listToStr(self):

        tests = [
            {'list': [1, 2, 3, 4, 5, 6], 'string': '1|2|3|4|5|6'},
            {'list': [9999], 'string': '9999'},
            {'list': [], 'string': ''},
            {'list': [1,'2','4',2.3], 'string': '1|2|4|2.3' }
        ]

        for test in tests:
            self.assertEqual(self.model._DBAdapter__listToStr(test['list']), test['string'])

    def test__getDimensions(self):
        tests = [
            {'string': 'Path:/data', 'key': 'Path', 'value': '/data'},
            {'string': 'path:/data,year:2010', 'key': 'year', 'value': '2010'},
            {'string': 'oops:tata,', 'key': 'oops', 'value': 'tata'},
            {'string': 'oops,', 'key': 'oops', 'value': ''},
            {'string': 'cores:(int)4,', 'key': 'cores', 'value': 4}
        ]

        for test in tests:
            self.assertEqual(self.model._DBAdapter__getDimensions(test['string'])[test['key']], test['value'])

    def test__retriveFormattedMetrics(self):
        a = [3, 5]
        all_metrics = self.model.getMetrics()

        data = self.model._DBAdapter__retriveFormattedMetrics(a, all_metrics)

        self.assertEqual(data[0]['name'], 'pewpewpew')
        self.assertEqual(data[1]['caption'], 'Hours')

    def test_importDataFromFile(self):

        def addELB(elb_name, metrics):
            values = {'test-elb': 1}
            _id = values[elb_name]

            if _id == 1:
                self.assertEqual(elb_name, 'test-elb')
                self.assertEqual(metrics, ['Latency|Seconds', 'RequestCount|Count'])

            return values[elb_name]

        def addInstance(instance_id, metrics):
            values = {'i-0001': 1, 'i-0002': 2, 'i-0003': 3, 'i-0004': 4, 'i-0005': 5, 'i-pew': 6}
            _id = values[instance_id]

            if _id in [1, 3]:
                self.assertEqual(metrics, ['test1', 'test2', 'test3||path:/data,year:2010'])

            elif _id in [1, 3]:
                self.assertEqual(metrics, ['test4', 'test5', 'test6||Path:/data'])

            return _id

        def addGroup(group_name, elb, instances):
            values = {'test-elb': 1, 'First Wave': 2}
            _id = values[str(group_name)]

            if _id == 1:
                self.assertEqual(elb, 1)
                self.assertEqual(instances, [1,3])
            elif _id == 2:
                self.assertEqual(elb, 0)
                self.assertEqual(instances, [4, 5, 6])

            return _id

        elbs = {
            'test-elb': _ELBs([_EC('i-0001'), _EC('i-0003')]),
        }

        self.model.addELB = addELB
        self.model.addInstance = addInstance
        self.model.addGroup = addGroup

        self.model.importDataFromFile(config, elbs)

    def test_addGroup(self):
        tests = [
            { 'uid': None, 'name': 'test1', 'elb': 999, 'instances': [4] },
            { 'uid': None, 'name': 'test2', 'elb': 1001, 'instances': [123, 129] },
            { 'uid': None, 'name': 'test1', 'elb': 999, 'instances': [124, 125, 120] }
        ]

        for test in tests:
            test['uid'] = self.model.addGroup(test['name'], test['elb'], test['instances'])

        groups = self.model.getGroups()
        _hash = {}

        for group in groups:
            _hash.update({str(group['uid']): group})

        for test in tests:
            item = _hash[str(test['uid'])]
            for key in ['name', 'instances', 'elb']:
                self.assertEqual(test[key], item[key])

    def test_addMetric(self):

        cases = [
            {
                'in': 'Latency|Seconds',
                'out': ('Latency', '', 'Seconds')
            },
            {
                'in': 'CPUUtilization|Count|Param:Test',
                'out': ('CPUUtilization', 'Param:Test', 'Count')
            },
            {
                'in': 'UsedSpacePercent||Path:/data',
                'out': ('UsedSpacePercent', 'Path:/data', 'Percent')
            },
            {
                'in': 'test||path:/data,year:2010',
                'out': ('test', 'path:/data,year:2010', 'Percent')
            }
        ]

        for case in cases:
            uid = self.model.addMetric(case['in'])
            result = self.__get('metrics', uid)
            self.assertEqual(result[1:], case['out'])


if __name__ == '__main__':
    unittest.main()

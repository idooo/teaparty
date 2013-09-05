__author__ = 'ido'

import sys
sys.path.append('../')

import unittest
from sqlite3 import OperationalError

from teaparty import model
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
                [1, '', 1, '1|2'],
                [2, 'new group', 0, '3|4|5']
            ],
            'elbs': [
                [1, 'test_bi_elb', '1|2']
            ],
            'instances': [
                [1, 'i-0001', '3|4'],
                [2, 'i-0003', '5|6'],
                [3, 'i-0004', '7|8'],
                [4, 'i-0005', '9|10'],
                [5, 'i-0006', '12|11'],
                [6, 'i-0007', '13|14']
            ],
            'metrics': [
                [1,"Latency", "", "Seconds" ],
                [2,"RequestCount",  "", "Count" ],
                [3,"pewpewpew", "", "Percent" ],
                [4,"UsedMemoryPercent", "", "Percent" ],
                [5,"UsedSpacePercent", "Path:/data", "Hours" ],
                [6,"test", "path:/data,year:2010", "Percent" ],
                [7,"pewpewpew", "", "Percent" ],
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
            { 'uid': None, 'name': 'test1', 'elb': 1002, 'instances': [4] },
            { 'uid': None, 'name': 'test2', 'elb': 1001, 'instances': [123, 129] },
            { 'uid': None, 'name': 'test1', 'elb': 1003, 'instances': [124, 125, 120] }
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

        cursor = self.model.connection.cursor()
        cursor.execute('DELETE FROM groups WHERE elb>=1000')
        self.model.connection.commit()

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

    def test_addELB(self):
        tests = [
            {'name': 'test_one_more', 'metrics': ['testELB1', 'testELB2'], 'uid': None},
            {'name': 'test_one_more', 'metrics': ['testELB2', 'testELB3'], 'uid': None},
            {'name': 'test_one_more1', 'metrics': ['testELB8', 'testELB7', 'add'], 'uid': None, 'duplicate': True},
            {'name': 'test_one_more2', 'metrics': ['testELB21'], 'uid': None},
            {'name': 'test_one_more1', 'metrics': [], 'uid': None, 'duplicate': True}
        ]

        for test in tests:
            test['uid'] = self.model.addELB(test['name'], test['metrics'])

        self.assertEqual(tests[0]['uid'], tests[1]['uid'])

        elbs = self.model.getELBs()
        for test in tests:
            elb = elbs[str(test['uid'])]
            self.assertEqual(test['name'], elb['name'])
            self.assertEqual(test['uid'], elb['uid'])

            if not 'duplicate' in test:
                self.assertEqual(len(test['metrics']), len(elb['metrics']))

    def test_addInstance(self):
        tests = [
            {'id': '11111', 'metrics': ['testINST1', 'testINST6'], 'uid': None},
            {'id': '22222', 'metrics': ['testINST2', 'testINST7'], 'uid': None},
            {'id': '33333', 'metrics': ['testINST3', 'testINST8', 'add'], 'uid': None},
            {'id': '11111', 'metrics': ['testINST3'], 'uid': None, 'duplicate': True},
            {'id': '22222', 'metrics': [], 'uid': None, 'duplicate': True}
        ]

        for test in tests:
            test['uid'] = self.model.addInstance(test['id'], test['metrics'])

        instances = self.model.getInstances()
        for test in tests:
            instance = instances[str(test['uid'])]
            self.assertEqual(test['id'], instance['id'])
            self.assertEqual(test['uid'], instance['uid'])

            if not 'duplicate' in test:
                self.assertEqual(len(test['metrics']), len(instance['metrics']))

    def test_add_get_MetricValues(self):
        cursor = self.model.connection.cursor()

        tests = [
            {'uid': 1, 'values': [
                {'timestamp': '2000-10-03 10:30', 'value': 0.13},
                {'timestamp': '2000-10-03 10:32', 'value': 0.23}
            ]},
            {'uid': 2, 'values': [
                {'timestamp': '2001-10-03 10:30', 'value': 0.33},
                {'timestamp': '2001-10-03 10:32', 'value': 0.43}
            ]},
            {'uid': 1, 'values': [
                {'timestamp': '2001-10-03 10:30', 'value': 0.53},
            ]},
            {'uid': 3, 'values': [
                {'timestamp': '2002-10-03 10:30', 'value': 0.73},
            ]},
            {'uid': 1, 'values': [
                {'timestamp': '1984-10-03 10:30', 'value': 0.63},
            ]}
        ]

        for test in tests:
            self.model.addMetricValues(test['uid'], test['values'], cursor=cursor)

        self.model.connection.commit()

        metric_values = self.model.getMetricValues(1, '2000', cursor)
        self.assertEqual(3, len(metric_values))

    def test_getLastMetricValueDate(self):
        cursor = self.model.connection.cursor()
        cursor.execute('DELETE FROM metric_values WHERE value>0')

        tests = [
            {'uid': 100, 'values': [
                {'timestamp': '2000-10-03 10:30', 'value': 0.11},
                {'timestamp': '2000-10-03 10:32', 'value': 0.21}
            ]},
            {'uid': 200, 'values': [
                {'timestamp': '2001-10-03 10:30', 'value': 0.31},
                {'timestamp': '2001-10-03 10:32', 'value': 0.41}
            ]},
            {'uid': 100, 'values': [
                {'timestamp': '2010-12-12 0:00', 'value': 0.51},
            ]},
            {'uid': 300, 'values': [
                {'timestamp': '2002-10-03 10:30', 'value': 0.71},
            ]},
            {'uid': 100, 'values': [
                {'timestamp': '1984-10-03 10:30', 'value': 0.61},
            ]}
        ]

        for test in tests:
            self.model.addMetricValues(test['uid'], test['values'], cursor=cursor)
        self.model.connection.commit()

        self.assertEqual(self.model.getLastMetricValueDate(100), '2010-12-12 0:00')
        self.assertEqual(self.model.getLastMetricValueDate(200), '2001-10-03 10:32')

    def test_deleteOldMetricValues(self):
        cursor = self.model.connection.cursor()
        cursor.execute('DELETE FROM metric_values WHERE value>0')

        tests = [
            {'uid': 1, 'values': [
                {'timestamp': '2000-10-03 10:31', 'value': 0.12},
                {'timestamp': '2000-10-03 10:32', 'value': 0.22},
                {'timestamp': '2000-10-03 10:33', 'value': 0.62},
            ]},
            {'uid': 2, 'values': [
                {'timestamp': '2001-10-03 10:30', 'value': 0.32},
                {'timestamp': '2001-10-03 10:32', 'value': 0.42}
            ]},
            {'uid': 3, 'values': [
                {'timestamp': '2002-10-03 10:30', 'value': 0.72},
            ]},
            {'uid': 1, 'values': [
                {'timestamp': '1984-10-03 10:30', 'value': 0.62},
            ]}
        ]

        for test in tests:
            self.model.addMetricValues(test['uid'], test['values'], cursor=cursor)

        self.model.connection.commit()

        self.model.deleteOldMetricValues('2000-10-03 10:32')
        metric_values = self.model.getMetricValues(1, '1900', cursor)
        self.assertEqual(len(metric_values), 2)

    def test_reflectStructure(self):
        structure = self.model.reflectStructure()

        self.assertEqual(structure[0]['type'], 'elb')
        self.assertEqual(structure[0]['name'], 'test_bi_elb')
        self.assertEqual(len(structure[0]['instances']), 2)

        self.assertEqual(structure[1]['type'], 'block')
        self.assertEqual(structure[1]['name'], 'new group')
        self.assertEqual(len(structure[1]['instances']), 3)


if __name__ == '__main__':
    unittest.main()

__author__ = 'ido'

from sys import path
path.append('../')

import unittest

from teaparty import model
from mock import Mock

class ModelTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.model = model.DBAdapter(':memory:')

    def __get(self, table_name, uid):
        c = self.model.connection.cursor()
        c.execute('SELECT * FROM {0} WHERE uid={1}'.format(table_name, uid))
        return c.fetchone()

    def test__initTables(self):
        c = self.model.connection.cursor()

        for table in self.model.format:
            c.execute("SELECT * FROM " + table['name'])

        self.assertEqual(True, True)


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

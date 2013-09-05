__author__ = 'ashteinikov'

import sys
sys.path.append('../')

import unittest

from teaparty import executor
from mock import Mock

class ExecutorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        def mocker():
            pass

        queue = []

        self.e = executor.Executor(mocker, queue)

    def test_aa(self):
        self.assertTrue(1)
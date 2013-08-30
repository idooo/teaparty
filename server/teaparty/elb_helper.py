# -*- coding: UTF-8 -*-

"""
AWS ELB wrapper based on boto for high-level operations
with Elastic Load Balancers
"""

import boto.ec2.elb

class ELBHelper():

    conn = False

    def __init__(self, region):
        self.connect(region)

    def connect(self, region):
        """
        Create AWS ELB connection

        :type region: string
        :param region: Region to connect
        """

        self.conn = boto.ec2.elb.connect_to_region(region)

    def getLoadBalancers(self):
        """
        Get load balancers and format it in friendly format

        :rtype: :dict
        :returns: Dictionary ELB name => ELB data
        """
        elbs = {}
        _raws = self.conn.get_all_load_balancers()
        for _raw in _raws:
            elbs.update({
                _raw.name: _raw
            })

        return elbs

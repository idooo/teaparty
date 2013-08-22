# -*- coding: UTF-8 -*-

import boto.ec2.elb

class ELBHelper():

    conn = False

    def __init__(self, region):
        self.connect(region)

    def connect(self, region):
        """
            Create connection to region
            If region didn't specified - connect to default region
            @param region
        """

        self.conn = boto.ec2.elb.connect_to_region(region)

    def getLoadBalancers(self):
        elbs = {}
        _raws = self.conn.get_all_load_balancers()
        for _raw in _raws:
            elbs.update({
                _raw.name: _raw
            })

        return elbs

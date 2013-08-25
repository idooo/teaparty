# -*- coding: UTF-8 -*-

import boto.ec2.cloudwatch
import datetime

class CloudWatchHelper():

    __ec2_metrics = {}

    # alarm states
    __ALARM_STATES = set(['OK', 'ALARM', 'INSUFFICIENT_DATA'])

    conn = False

    def __init__(self, region):
        self.connect(region)

    def connect(self, region):
        """
            Create connection to region
            If region didn't specified - connect to default region
            @param region
        """

        self.conn = boto.ec2.cloudwatch.connect_to_region(region)

        if not self.conn:
            print 'Invalid region name'
            return False

    def getMetricData(self, metric_name, namespace, dimensions, unit, statistics='Average', minutes=15, period=60):
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=minutes)
        return self.conn.get_metric_statistics(period, start_time, end_time, metric_name, namespace, statistics, dimensions=dimensions, unit=unit)

    def getMetrics(self, filter=None, namespace=None, dimensions=None):
        return self.conn.list_metrics(metric_name=filter, namespace=namespace, dimensions=dimensions)
    
    def getAlarms(self):
        _raw = self.conn.describe_alarms()
        alarms = {}

        if not _raw:
            return alarms

        for alarm in _raw:
            alarms.update({
                alarm.name: alarm
            })

        return alarms

    def getAlarm(self, alarm_name):
        if not isinstance(alarm_name, list):
            alarm_name = [alarm_name]

        alarm = self.conn.describe_alarms(alarm_names=alarm_name)
        if not alarm:
            raise Exception('Alarm does not exist')

        return alarm[0]

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

    def __prepareParams(self, instances_ids, start_time, end_time, stats_names):
        if not start_time or not isinstance(start_time, datetime):
            start_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=600)

        if not end_time or not isinstance(end_time, datetime):
            end_time =  datetime.datetime.utcnow()

        if not isinstance(stats_names, list):
            stats_names = [stats_names]

        if not isinstance(instances_ids, list):
            instances_ids = [instances_ids]

        return (instances_ids, start_time, end_time, stats_names)

    def getMetricData(self, metric, statistics='Average'):
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=60)
        return metric.query(start_time, end_time, statistics, unit='Percent', period=60)

    def getMetrics(self, filter, namespace=None, dimensions=None):
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

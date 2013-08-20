# -*- coding: UTF-8 -*-

import boto.ec2.cloudwatch
import datetime

class CloudWatchHelper():

    __ec2_metrics = {}

    # alarm states
    __ALARM_STATES = set(['OK', 'ALARM', 'INSUFFICIENT_DATA'])

    REGION = 'ap-southeast-2'

    ZONE = 'ap-southeast-2a'
    RESERVED_ZONE = 'ap-southeast-2b'

    conn = False

    def __init__(self, region=False):
        if region:
            self.REGION = region

        self.connect(region)

    def connect(self, region = False):
        """
            Create connection to region
            If region didn't specified - connect to default region
            @param region
        """
        if not region:
            region = self.REGION

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

    def getInstancesMetric(self, instances_ids, metric_name, stats_names, period=60, start_time=None, end_time=None):
        metrics = {}

        (instances_ids, start_time, end_time, stats_names) = self.__prepareParams(instances_ids, start_time, end_time, stats_names)

        for instance_id in instances_ids:

            if isinstance(instance_id, ProtoInstance):
                instance_id = instance_id['id']

            result = self.conn.get_metric_statistics(
                period,
                start_time,
                end_time,
                metric_name,
                self._ns_EC2,
                stats_names,
                dimensions={'InstanceId': [instance_id]}
            )

            if result:
                result = result[0]
            else:
                result = {}

            metrics.update({
                instance_id : result
            })

        if metrics:
            if len(instances_ids) == 1:
                return metrics[instances_ids[0]]

        return metrics

    def getInstanceMetric(self, instance_id, metric_name, stats_names, period=60, start_time=None, end_time=None):
        """
            Get metric data for instance
            @param instance_id {str|dict}
        """
        return self.getInstancesMetric(instance_id, metric_name, stats_names, period=period, start_time=start_time, end_time=end_time)

    def getMetrics(self, filter, namespace=None):
        return self.conn.list_metrics(metric_name=filter, namespace=namespace)
    
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

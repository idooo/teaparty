"""
AWS Cloudwatch wrapper based on boto for high-level operations
with metrics and alarms
"""

import boto.ec2.cloudwatch
import datetime

class CloudWatchHelper():

    conn = False

    def __init__(self, region):
        self.connect(region)

    def connect(self, region):
        """
        Create AWS Cloudwatch connection

        :type region: string
        :param region: Region to connect
        """

        self.conn = boto.ec2.cloudwatch.connect_to_region(region)

        if not self.conn:
            raise Exception('Invalid region name')
            return False

    def getMetricData(self, metric_name, namespace, dimensions, unit, statistics='Average', minutes=15, period=60):
        """
        Wrapper for boto Cloudwatch get_metric_statistics, but with predifined
        end time (= current) and start tame calculated by delta.
        Use this method to get metric data for last N minutes

        :type metric_name: string
        :param metric_name: AWS metric name to get data

        :type namespace: string
        :param namespace: AWS namespace for metric

        :type dimensions: dict
        :param dimensions: AWS metric dimensions

        :type unit: string
        :param unit: AWS metric unit (for example, Percent/Seconds/Count/...)

        :type statistics: string
        :param statistics: AWS statistics name (for example, Average/Sum/...)

        :type minutes: integer
        :param minutes: Amount of time in minutes to get data (last N minutes)

        :type period: integer
        :param period: AWS period

        :rtype: :list
        :returns: List of metric datapoints
        """
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=minutes)
        return self.conn.get_metric_statistics(period, start_time, end_time, metric_name, namespace, statistics, dimensions=dimensions, unit=unit)

    def getMetrics(self, filter=None, namespace=None, dimensions=None):
        """
        Wrapper for boto Cloudwatch list_metrics
        """
        return self.conn.list_metrics(metric_name=filter, namespace=namespace, dimensions=dimensions)
    
    def getAlarms(self):
        _raw = self.conn.describe_alarms()
        result = {
            'count': 0,
            'statuses': []
        }

        if _raw:
            alarms = []
            for alarm in _raw:
                alarms.append({
                    'name': alarm.name,
                    'status': alarm.state_value
                })

            result['statuses'] = alarms

        return result

    def getAlarm(self, alarm_name):
        if not isinstance(alarm_name, list):
            alarm_name = [alarm_name]

        alarm = self.conn.describe_alarms(alarm_names=alarm_name)
        if not alarm:
            raise Exception('Alarm does not exist')

        return alarm[0]

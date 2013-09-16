
import imp
import sqlite3
import os
import sys
import re
from datetime import datetime, timedelta
from helpers import cache
import logging

class DBAdapter():

    connection = None
    counters = {}

    RE_INT = re.compile(r'\(int\)(.*)', re.I+re.U)

    DEFAULT_UNIT = 'Percent'

    # TODO: Need to store max/min graph values for metrics
    # TODO: Auto select max/min values for % (0,100)
    # TODO: Add baseline

    format = [
        {
            'name': 'groups',
            'fields': ['uid integer', 'name text', 'elb integer', 'instances text']
        },
        {
            'name': 'elbs',
            'fields': ['uid integer', 'name text', 'metrics text']
        },
        {
            'name': 'instances',
            'fields': ['uid integer', 'id text', 'metrics text']
        },
        {
            'name': 'metrics',
            'fields': ['uid integer', 'name text', 'dimensions text', 'unit text', 'caption text', 'show_units text']
        },
        {
            'name': 'metric_values',
            'fields': ['metric_uid integer', 'date text', 'value float']
        }
    ]

    def __init__(self, dbname='teaparty.db'):

        self.logger = logging.getLogger('tparty.model')

        if dbname == ':memory:':
            self.connection = sqlite3.connect(dbname)
        else:
            _ROOT = os.path.abspath(os.path.dirname(__file__))
            self.connection = sqlite3.connect(os.path.join(_ROOT, 'db', dbname))

        self.__initTables()
        self.getCounters()

    def __initTables(self):
        c = self.connection.cursor()
        for table in self.format:
            fields = ','.join(table['fields'])
            query = 'create table if not exists {0} ({1})'.format(table['name'], fields)

            c.execute(query)

        self.connection.commit()

    def __uid(self, counter_name):
        if not counter_name in self.counters:
            self.counters[counter_name] = 0

        self.counters[counter_name] += 1
        return self.counters[counter_name]

    def __isExist(self, table_name, search):
        c = self.connection.cursor()
        query = 'SELECT uid FROM "{0}" WHERE {1}'.format(table_name, search)
        c.execute(query)

        result = c.fetchone()
        if result:
            return result[0]

        return False

    def __listToStr(self, items):
        if items:
            result = '|'.join(map(str, items))
        else:
            result = ''

        return result

    def __getDimensions(self, dim_string):
        result = {}

        if dim_string:
            items = dim_string.split(',')

            for item in items:
                tmp = item.split(':')
                if len(tmp) <= 1:
                    tmp.append('')

                else:
                    pos = re.search(self.RE_INT, tmp[1])
                    if pos:
                        tmp[1] = int(pos.group(1))

                result.update({tmp[0]: tmp[1]})

        return result

    def __retriveFormattedMetrics(self, metrics_ids, all_metrics):
        metrics = []

        for metric_id in metrics_ids:
            str_metric_id = str(metric_id)

            if str_metric_id in all_metrics:
                metrics.append({
                    'name': all_metrics[str_metric_id]['name'],
                    'caption': all_metrics[str_metric_id]['caption'],
                    'show_units': all_metrics[str_metric_id]['show_units'],
                    'unit': all_metrics[str_metric_id]['unit'],
                    'uid': metric_id
                })

            else:
                self.logger.warn('Metric not found: __retriveFormattedMetrics, ' + str_metric_id)

        return metrics

    def clearTables(self):
        c = self.connection.cursor()
        for table in self.format:
            query = 'DELETE FROM {0}'.format(table['name'])

            c.execute(query)

        self.connection.commit()

    def getCounters(self):
        c = self.connection.cursor()

        self.counters = {}
        for table in self.format:
            try:
                c.execute("SELECT MAX(uid) FROM " + table['name'])
                result = c.fetchone()
                if result[0]:
                    value = int(result[0])
                else:
                    value = 0
            except sqlite3.OperationalError:
                value = 0

            self.counters[table['name']] = value

    def addMetric(self, metric_name):

        # metric_name | dimensions | units | display name | display units

        c = self.connection.cursor()

        parts = metric_name.split('|', 5)
        metric_name = parts[0]

        params = [
            '', # dimensions
            self.DEFAULT_UNIT, # unit
            metric_name, # display name
            '' # display units
        ]

        for i in range(1, len(parts)):
            part = parts[i].strip()
            if part:
                params[i-1] = part

        metric_id = self.__uid('metrics')

        query = 'INSERT INTO metrics VALUES ({0}, "{1}", "{2}", "{3}", "{4}", "{5}")'\
            .format(metric_id, metric_name, params[0], params[1], params[2], params[3])

        c.execute(query)

        return metric_id

    def addMetrics(self, metrics):
        metric_ids = []
        for metric in metrics:
            _id = self.addMetric(metric)
            if _id:
                metric_ids.append(_id)

        return metric_ids

    def addELB(self, elb_name, metrics):
        c = self.connection.cursor()

        result = self.__isExist('elbs', 'name="'+elb_name+'"')

        if not result:
            metric_ids = self.__listToStr(self.addMetrics(metrics))
            elb_uid = self.__uid('elbs')

            query = 'INSERT INTO elbs VALUES ({0}, "{1}", "{2}")'.format(elb_uid, elb_name, metric_ids)
            c.execute(query)

            self.connection.commit()

            return elb_uid

        return result

    def addInstance(self, instance_id, metrics):
        c = self.connection.cursor()

        result = self.__isExist('instances', 'id="'+instance_id+'"')

        if not result:
            metric_ids = self.__listToStr(self.addMetrics(metrics))
            instance_uid = self.__uid('instances')

            query = 'INSERT INTO instances VALUES ({0}, "{1}", "{2}")'.format(instance_uid, instance_id, metric_ids)
            c.execute(query)

            self.connection.commit()

            return instance_uid

        return result

    def addGroup(self, group_name, elb, instances, cursor=None):
        if not cursor:
            cursor = self.connection.cursor()

        instances_ids = self.__listToStr(instances)
        group_uid = self.__uid('groups')

        query = 'INSERT INTO groups VALUES ({0}, "{1}", {2}, "{3}")'.format(group_uid, group_name, elb, instances_ids)
        cursor.execute(query)

        self.connection.commit()

        return group_uid

    def updateGroup(self, group_name, elb, instances):
        # TODO: update group logic
        pass

    def addMetricValues(self, metric_uid, values, cursor=None):
        # It's better for performance to pass cursor instead create new
        if not cursor:
            cursor = self.connection.cursor()

        str_metric_uid = str(metric_uid)
        formatted_values = []
        for item in values:
            formatted_values.append('(' + str_metric_uid + ',"' + item['timestamp'] + '","' + str(item['value'])+'")')

        query = 'INSERT INTO metric_values VALUES {0}'.format(','.join(formatted_values))
        return cursor.execute(query)

    def getMetrics(self):
        _hash = {}
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM metrics'):
            dimensions = self.__getDimensions(row[2])
            caption = row[4].split(':', 2)

            _hash.update({
                str(row[0]) : {
                    'uid': row[0],
                    'name': row[1],
                    'dimensions': dimensions,
                    'unit': row[3],
                    'caption': caption,
                    'show_units': row[5]
                }
            })

        return _hash

    def getInstances(self):
        _hash = {}
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM instances'):
            _hash.update({
                str(row[0]) : {
                    'uid': row[0],
                    'id': row[1],
                    'metrics': map(int, row[2].split('|'))
                }
            })

        return _hash

    def getELBs(self):
        _hash = {}
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM elbs'):
            _hash.update({
                str(row[0]) : {
                    'uid': row[0],
                    'name': row[1],
                    'metrics': map(int, row[2].split('|'))
                }
            })

        return _hash

    def getGroups(self):
        _results = []
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM groups'):
            _results.append({
                    'uid': row[0],
                    'name': row[1],
                    'elb': row[2],
                    'instances': map(int, row[3].split('|'))
            })

        return _results

    def getLastMetricValueDate(self, uid, cursor=None):
        # It's better for performance to pass cursor instead create new
        if not cursor:
            cursor = self.connection.cursor()

        cursor.execute("SELECT MAX(date) FROM metric_values WHERE metric_uid={0}".format(uid))
        result = cursor.fetchone()
        if result[0]:
            value = result[0]
        else:
            value = ''

        return value

    def getMetricValues(self, metric_uid=None, date=None, limit=None, sort='date', cursor=None):
        if not cursor:
            cursor = self.connection.cursor()

        metric_values = []

        where = []
        if metric_uid:
            where.append('metric_uid=' + str(metric_uid))

        if date:
            where.append('date>="' + date + '"')

        if where:
            query = 'SELECT * FROM metric_values WHERE {0} ORDER BY {1} '.format(' AND '.join(where), sort)

        if limit:
            query += ' LIMIT ' + str(limit)

        rows = cursor.execute(query)

        if rows:
            for row in rows:
                metric_values.append(row)

        return metric_values

    def getAllMetricValues(self, count=50, cursor=None):
        if not cursor:
            cursor = self.connection.cursor()

        metrics = self.getMetrics()
        result = {}

        for str_metric_uid in metrics:
            metric_values = self.getMetricValues(metrics[str_metric_uid]['uid'], limit=count, cursor=cursor)
            result.update({str_metric_uid: metric_values})

        return result

    def deleteOldMetricValues(self, time_value=7, cursor=None):

        if not cursor:
            cursor = self.connection.cursor()

        if isinstance(time_value, int):
            last_time = datetime.utcnow() - timedelta(days=time_value)
            time_value = datetime.strftime(last_time, '%Y-%m-%d')

        query = 'DELETE FROM metric_values WHERE date<"{0}"'.format(time_value)
        cursor.execute(query)

        self.connection.commit()

    @cache
    def reflectStructure(self):

        groups = self.getGroups()
        elbs = self.getELBs()
        all_instances = self.getInstances()
        all_metrics = self.getMetrics()

        result = []

        for group in groups:
            block = {
                'name': group['name'],
                'type': 'block',
                'instances': []
            }

            if group['elb']:
                if str(group['elb']) in elbs:

                    elb = elbs[str(group['elb'])]
                    block.update({
                        'name': elb['name'],
                        'type': 'elb',
                        'metrics': self.__retriveFormattedMetrics(elb['metrics'], all_metrics)
                    })

                else:
                    self.logger.warn('ELB not found: reflectStructure, ' + str(group['elb']))

            instances = []
            for instance_id in group['instances']:
                str_instance_id = str(instance_id)

                if str_instance_id in all_instances:
                    instance = all_instances[str_instance_id]

                    instances.append({
                        'id': instance['id'],
                        'metrics': self.__retriveFormattedMetrics(instance['metrics'], all_metrics)
                    })

            block.update({
                'instances': instances
            })

            result.append(block)

        return result

    def importDataFromFile(self, config, elbs={}):

        if not isinstance(config, list):
            try:
                config_module = imp.load_source('config', config)
                config = config_module.config
            except Exception:
                print "Config file %s not found." % config
                sys.exit(1)

        for obj in config:

            if not 'type' in obj or obj['type'] == 'block':
                elb_uid = 0
                instances_uids = []
                for instance in obj['instances']:
                    instances_uids.append(self.addInstance(instance, obj['metrics']))

            # Load balancer logic
            elif obj['type'] == 'elb':

                if not obj['name'] in elbs:
                    raise Exception('There is not ELB with name ' + obj['name'])

                obj['instances'] = elbs[obj['name']].instances[:]

                elb_uid = self.addELB(obj['name'], obj['metrics'])
                instances_uids = []
                for instance in obj['instances']:
                    instances_uids.append(self.addInstance(instance.id, obj['child_metrics']))


            result = self.__isExist('groups', 'name="' + obj['name'] +'"')
            if result:
                self.updateGroup(obj['name'], elb_uid, instances_uids)

            else:
                self.addGroup(obj['name'], elb_uid, instances_uids)

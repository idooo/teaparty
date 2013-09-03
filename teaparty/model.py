
import imp
import sqlite3
import os
import sys
import re

class DBAdapter():

    connection = None
    counters = {}

    RE_INT = re.compile(r'\(int\)(.*)', re.I+re.U)

    DEFAULT_UNIT = 'Percent'

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
            'fields': ['uid integer', 'name text', 'dimensions text', 'unit text']
        },
        {
            'name': 'metric_values',
            'fields': ['metric_uid integer', 'date text', 'value float']
        }
    ]

    def __init__(self, dbname='teaparty.db'):
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
                    'caption': all_metrics[str_metric_id]['unit'],
                    'units': '__',
                    'uid': metric_id
                })

            # TODO: what we will do?
            else:
                pass

        return metrics

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
        c = self.connection.cursor()

        dimensions = ''
        unit = self.DEFAULT_UNIT

        parts = metric_name.split('|', 3)
        metric_name = parts[0]
        if len(parts) > 1:
            if parts[1]:
                unit = parts[1]
            if len(parts) > 2:
                dimensions = parts[2]

        metric_id = self.__uid('metrics')

        query = 'INSERT INTO metrics VALUES ({0}, "{1}", "{2}", "{3}")'\
            .format(metric_id, metric_name, dimensions, unit)

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

    def addGroup(self, elb, instances):

        instances_ids = self.__listToStr(instances)

        c = self.connection.cursor()

        # If group has ELB
        if elb:
            result = self.__isExist('groups', 'elb='+str(elb)+'')
            if not result:
                group_uid = self.__uid('groups')

                query = 'INSERT INTO groups VALUES ({0}, "", {1}, "{2}")'.format(group_uid, elb, instances_ids)
                c.execute(query)

                self.connection.commit()

                return group_uid

            else:
                pass
                # TODO: Update existing

        elif instances_ids:

            # TODO: add logic
            # if there is not ELB in group

            result = self.__isExist('groups', 'instances="'+instances_ids+'"')
            if result:
                pass
            else:
                # Update current group
                pass


        else:
            raise Exception("Empty group")

    def addMetricValues(self, metric_uid, values, cursor=None):
        # It's better for performance to pass cursor instead create new
        if not cursor:
            cursor = self.connection.cursor()

        str_metric_uid = str(metric_uid)
        formatted_values = []
        for item in values:
            formatted_values.append('(' + str_metric_uid + ',"' + item['timestamp'] + '","' + str(item['value'])+'")')

        query = 'INSERT INTO metric_values VALUES {0}'.format(','.join(formatted_values))
        cursor.execute(query)

    def getMetrics(self):
        _hash = {}
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM metrics'):
            dimensions = self.__getDimensions(row[2])
            _hash.update({
                str(row[0]) : {
                    'uid': row[0],
                    'name': row[1],
                    'dimensions': dimensions,
                    'unit': row[3]
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

    def getLastMetricValue(self, uid, cursor=None):
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

    def getMetricValues(self, metric_uid=None, date=None, cursor=None):
        if not cursor:
            cursor = self.connection.cursor()

        metric_values = []

        date_filter = ''
        if date:
            date_filter = 'WHERE date>="' + date + '"'

        query = 'SELECT * FROM metric_values {0} ORDER BY date'.format(date_filter)

        if metric_uid:
            query += ' WHERE metric_uid=' + str(metric_uid)

        for row in cursor.execute(query):
            metric_values.append(row)

        return metric_values

    def deleteOldMetricValues(self, last_time, cursor=None):
        if not cursor:
            cursor = self.connection.cursor()

        query = 'DELETE FROM metric_values WHERE date<{0}'.format(last_time)
        cursor.execute(query)

    def reflectStructure(self):

        groups = self.getGroups()
        elbs = self.getELBs()
        all_instances = self.getInstances()
        all_metrics = self.getMetrics()

        result = []

        for group in groups:
            block = {
                'name': '',
                'type': 'block',
                'instances': []
            }

            if group['elb']:
                elb = elbs[str(group['elb'])]
                block.update({
                    'name': elb['name'],
                    'metrics': self.__retriveFormattedMetrics(elb['metrics'], all_metrics)
                })

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

        if not isinstance(config, dict):
            try:
                config_module = imp.load_source('config', config)
                config = config_module.config
            except Exception:
                print "Config file %s not found." % config
                sys.exit(1)

        # TODO: Error handling
        for obj in config:

            # Load balancer logic
            if obj['type'] == 'elb':

                if not obj['name'] in elbs:
                    raise Exception('There is not ELB with name ' + obj['name'])

                obj['instances'] = elbs[obj['name']].instances[:]

                elb_uid = self.addELB(obj['name'], obj['metrics'])
                instances_uids = []

                for instance in obj['instances']:
                    instances_uids.append(self.addInstance(instance.id, obj['child_metrics']))

                self.addGroup(elb_uid, instances_uids)









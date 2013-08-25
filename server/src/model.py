import sqlite3

class DBAdapter():

    connection = None
    counters = {}

    DEFAULT_UNIT = 'Percent'

    format = [
        {
            'name': 'groups',
            'fields': ['uid integer', 'elb integer', 'instances text']
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
            'fields': ['uid integer', 'name text', 'unit text', 'dimensions text']
        },
        {
            'name': 'metric_values',
            'fields': ['metric_uid integer', 'value float']
        }
    ]

    def __init__(self, dbname):
        self.connection = sqlite3.connect(dbname)
        self.__initTables()
        self.__getCounters()

    def __initTables(self):
        c = self.connection.cursor()
        for table in self.format:
            fields = ','.join(table['fields'])
            query = 'create table if not exists {0} ({1})'.format(table['name'], fields)

            c.execute(query)

        self.connection.commit()

    def __getCounters(self):
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
                # TODO: Format tmp[1] (int), {str)
                result.update({tmp[0]: tmp[1]})

        return result

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

                query = 'INSERT INTO groups VALUES ({0}, {1}, "{2}")'.format(group_uid, elb, instances_ids)
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

    def getMetrics(self):
        _hash = {}
        c = self.connection.cursor()
        for row in c.execute('SELECT * FROM metrics'):
            dimensions = self.__getDimensions(row[2])
            _hash.update({
                str(row[0]) : {
                    'uid': row[0],
                    'name': row[1],
                    'dimensions': dimensions
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
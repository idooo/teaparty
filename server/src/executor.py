import threading
from time import sleep
from datetime import datetime
from src.model import DBAdapter


class ExecutorThread(threading.Thread):
    name = ''

    def __init__(self, parent, name):
        self.name = name
        self.parent = parent
        threading.Thread.__init__(self)

    def run(self):
        while True:

            if self.parent.state == 0:
                break

            if self.parent.state == 2:
                sleep(5)

            elif self.parent.state == 1:
                if not self.parent.local_queue.ended:
                    item = self.parent.local_queue.get()

                    # TODO: Handle AWS errors
                    datapoints = self.parent.proc(item['name'], item['namespace'], item['dimensions'], item['unit'])
                    self.parent.result_pool.append({str(item['uid']): datapoints})

                    sleep(self.parent.latency)
                else:
                    if self.parent.debug:
                        print self.name + ' is waiting...'

                    sleep(1)


class myQueue(list):
    cursor = 0
    body = []

    ended = False

    def add(self, items):
        if isinstance(items, list):
            for item in items:
                self.body.append(item)
        else:
            self.body.append(items)

    def next(self):
        self.cursor += 1
        if self.cursor == len(self.body):
            self.cursor = 0
            self.ended = True

    def get(self):
        result = self.body[self.cursor]
        self.next()
        return result

    def renew(self):
        self.ended = False


class Executor():
    threads = {}
    threads_number = 0

    state = 0
    latency = 1
    time_between = 15

    debug = False

    proc = None
    local_queue = None

    result_pool = []

    def __init__(self, proc, items, dbname, latency=1, debug=False):
        self.local_queue = myQueue()
        self.local_queue.add(items)
        self.latency = latency
        self.proc = proc
        self.debug = debug

        self.db = self.db = DBAdapter(dbname)

        # To prevent strptime thread errors
        datetime.strptime('1000', '%Y')

    def startThread(self, name):
        self.threads.update({name: ExecutorThread(self, name)})
        self.threads[name].start()

    def execute(self, threads):
        self.state = 1
        for i in range(0, threads):
            self.threads_number += 1
            name = 'Thread_' + str(self.threads_number)
            self.startThread(name)

        if not self.debug:
            while True:
                if self.local_queue.ended:
                    self.saveDataFromPool()
                    self.result_pool = []
                    self.local_queue.renew()

                sleep(self.time_between)
        else:
            while not self.local_queue.ended:
                sleep(1)

            self.stop()
            self.saveDataFromPool()


    def stop(self):
        self.state = 0

    def pause(self):
        if self.state == 1:
            self.state = 2

    def resume(self, threads=4):
        if self.state == 2:
            self.state == 1

        elif self.state == 0:
            self.execute(threads)

    def __getMetricStatName(self, datapoint):
        for key in datapoint.keys():
            if not key in ['Timestamp', 'Unit']:
                return key

    def saveDataFromPool(self):
        data = self.result_pool[:]

        # It's better for performance to pass cursor instead create new
        c = self.db.connection.cursor()

        for metric in data:
            metric_uid = int(metric.keys()[0])
            datapoints = metric[str(metric_uid)]

            if not datapoints:
                continue

            stat_name = self.__getMetricStatName(datapoints[0])

            last_metric_date = self.db.getLastMetricValue(metric_uid, cursor=c)

            new_points = []
            for point in datapoints:
                timestamp = datetime.strftime(point['Timestamp'], '%Y-%m-%d %H:%M:%S')
                if timestamp > last_metric_date:
                    new_points.append({'timestamp':timestamp, 'value': point[stat_name]})

            # TODO: May be sort points by timestamp before add to database?
            if new_points:
                self.db.addMetricValues(metric_uid, new_points, c)
                self.db.connection.commit()

            # TODO: Delete outdated (1d-3d records)

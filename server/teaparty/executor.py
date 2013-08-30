"""
Classes to provide multithread support for getting data from AWS.

Executor gets data during initialisation in queue format,
then starts several threads to process queue. When queue ended,
executor will save all data, pause all threads for a while 
and start jobs again. 
"""

import threading
from time import sleep
from datetime import datetime
from teaparty.model import DBAdapter


class ExecutorThread(threading.Thread):
    """
    Thread class (worker) to get data from AWS in multithread mode.
    Get important data from parent object (executor)
       local_queue - queue with tasks information
       state - global state of parent
    """
    name = ''

    def __init__(self, parent, name):
        self.name = name
        self.parent = parent
        threading.Thread.__init__(self)

    def run(self):
        """ Main process for getting data from AWS """
        while True:

            # State 0 == stop work
            if self.parent.state == 0:
                break

            # State 2 == wait
            if self.parent.state == 2:
                sleep(5)

            # State 1 == work
            elif self.parent.state == 1:

                if not self.parent.local_queue.ended:
                    item = self.parent.local_queue.get()

                    try:
                        datapoints = self.parent.proc(item['name'], item['namespace'], item['dimensions'], item['unit'])
                        self.parent.result_pool.append({str(item['uid']): datapoints})
                    except Exception:
                        # TODO: Print data somewhere
                        pass

                    sleep(self.parent.latency)

                else:
                    if self.parent.debug:
                        print self.name + ' is waiting...'

                    sleep(1)


class myQueue(list):
    """
    Class to store tasks. Workers get task data from queue
    by reading data by cursor and moving this cursor after each read
    """
    cursor = 0
    body = []

    ended = False

    def add(self, items):
        """ 
        Add list of items to queue 

        :type items: list
        :param items: list of items to add to queue
        """
        if isinstance(items, list):
            for item in items:
                self.body.append(item)
        else:
            self.body.append(items)

    def next(self):
        """
        Move cursor to next position. Mark queue as ended 
        if cursor was moved to the last position of queue
        """
        self.cursor += 1
        if self.cursor == len(self.body):
            self.cursor = 0
            self.ended = True

    def get(self):
        """
        Read element from queue and move cursor to the next position

        :rtype: :object
        :returns: Queue item
        """
        result = self.body[self.cursor]
        self.next()
        return result

    def renew(self):
        """ Renew queue to mark it as not ended"""
        self.ended = False


class Executor():
    """
    Main class to execute queue tasks, save received data to database
    """

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
        """
        :type proc: method
        :param proc: method to execute

        :type items: list
        :param items: tasks to process

        :type dbname: string
        :param dbname: path to sqlite database to store data

        :type latency: integer
        :param latency: Times in seconds between requests withing one thread

        :type debug: bool
        :param debug: Debug mode
        """
        self.local_queue = myQueue()
        self.local_queue.add(items)
        self.latency = latency
        self.proc = proc
        self.debug = debug

        self.db = self.db = DBAdapter(dbname)

        # To prevent strptime thread errors
        datetime.strptime('1000', '%Y')

    def __getMetricStatName(self, datapoint):
        for key in datapoint.keys():
            if not key in ['Timestamp', 'Unit']:
                return key

    def startThread(self, name="Noname"):
        """ Start thread with specific name """
        self.threads.update({name: ExecutorThread(self, name)})
        self.threads[name].start()

    def execute(self, threads):
        """ Start threads. Get and save data in infinite loop """
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

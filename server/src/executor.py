import threading
from time import sleep
from datetime import datetime


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
                item = self.parent.local_queue.get()
                if item:
                    datapoints = self.parent.proc(item['name'], item['namespace'], item['dimensions'])
                    self.parent.result_pool.append({str(item['uid']): datapoints})
                    sleep(self.parent.latency)
                else:
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

    def get(self):
        result = self.body[self.cursor]
        self.next()
        return result


class Executor():
    threads = {}
    threads_number = 0

    state = 0
    latency = 1

    proc = None
    local_queue = None

    result_pool = []

    def __init__(self, proc, items, latency=1):
        self.local_queue = myQueue()
        self.local_queue.add(items)
        self.latency = latency
        self.proc = proc

        # To prevent thread errors
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

    def getData(self):
        data = self.result_pool[:]
        self.result_pool = []
        return data


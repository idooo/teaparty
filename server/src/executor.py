import threading
from time import sleep


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
                    print self.name + ' is working... ' + str(item)
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

    local_queue = None

    def __init__(self, items, latency=1):
        self.local_queue = myQueue()
        self.local_queue.add(items)
        self.latency = latency

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
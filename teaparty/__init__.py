__version__ = 0.2

import sys
from time import time

if sys.argv[0] != 'setup.py':

    from ec2_helper import *
    from cloudwatch_helper import *
    from elb_helper import *
    from model import *
    from metric_queue import *
    from executor import *

    try:
        from sockets import *
    except Exception:
        pass

def cache(function):
    memo = None
    last_time = 0
    time_to_cache = 60

    def wrapper(*args):
        if time() < last_time + time_to_cache:
            return memo
        else:
            rv = function(*args)
            memo = rv
            return rv

    return wrapper

__version__ = 0.2

import sys
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

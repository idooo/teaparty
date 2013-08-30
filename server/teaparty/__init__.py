__version__ = 0.1

import sys
if sys.argv[0] != 'setup.py':

    from mocker import *
    from ec2_helper import *
    from cloudwatch_helper import *
    from elb_helper import *
    from model import *
    from executor import *

    try:
        from sockets import *
    except Exception:
        pass

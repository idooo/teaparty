from time import time

def cache(function):
    memo = {}
    time_to_cache = 60

    def wrapper(*args):
        if args in memo and time() < memo[args]['time'] + time_to_cache:
            return memo[args]['record']
        else:
            rv = function(*args)
            memo[args] = {
                'record': rv,
                'time': time()
            }
            return rv

    return wrapper
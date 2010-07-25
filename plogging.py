import logging, os, traceback


def log(*s):
    pass

# @see http://groups.google.com/group/comp.lang.python/msg/1c5774a7e4c57a06
def caller(up=0):
    '''Get file name, line number, function name and
    source text of the caller's caller as 4-tuple:
    (file, line, func, text).
    
    The optional argument 'up' allows retrieval of
    a caller further back up into the call stack.

    Note, the source text may be None and function
    name may be '?' in the returned result. In
    Python 2.3+ the file name may be an absolute
    path.
    '''
    try: # just get a few frames
        f = traceback.extract_stack(limit=up+2)
        if f:
            return f[0]
    except:
        pass
    # running with psyco?
    return ('', 0, '', None)


if os.environ["SERVER_SOFTWARE"].startswith("Development"): # local dev env.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    while len(logger.handlers):
        logger.handlers.pop()
    
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    
    def log(*s):
        fl, ln, fn, sr = caller(1)
        logging.warn(fl.split('/')[-1] + ' - ' + fn + ' - ' + str(ln) + ' ## ' + ' '.join([str(i) for i in s]))
        return

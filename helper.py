from datetime import datetime, time as dtime

def use_rth_now(now=None):
    now = now or datetime.now().time()
    if now < dtime(10, 0):
        return False
    return True



from watchl4d.website.lib import set_streams as ss
# from watchl4d.queue.queue import Queue
from watchl4d.queue.scheduler import Scheduler

def set_streams():
    print 'settings streams...'
    ss()
    # Queue().set_streams()
    Scheduler().schedule_set_streams()


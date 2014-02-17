# import os
# import sys
# import rq

# path = '/srv/www/blacklisted'
# if path not in sys.path:
#     sys.path.insert(0, path)

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "watchl4d.settings")




import datetime
import os
import sys
import rq
import time

from redis.exceptions import ConnectionError
from redis import Redis


def setup():
    dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, dir + '/../../')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'watchl4d.settings'

    # This should be set by supervisord.conf
    # if 'DJANGO_LOCAL_ENV' not in os.environ:
    #     os.environ['DJANGO_LOCAL_ENV'] = os.environ['USER']

def run():
    from django.conf import settings

    # from util import print_with_timestamp, get_queue_name

    connection = Redis(
        settings.REDIS_HOST, 
        settings.REDIS_PORT, 
        settings.REDIS_DB, 
        settings.REDIS_PASSWORD)

    with rq.Connection(connection):
        # Construct a single queue
        qs = [rq.Queue()]
        # Clear all old queue messages
        qs[0].empty()
        # Create a worker to monitor the queue and start it up
        w = rq.Worker(qs)
        print 'Running'
        w.work()

if __name__ == '__main__':
    setup()
    while True:
        try:
            run()
        except ConnectionError:
            print 'Unable to connect to redis! Trying to reconnect.'
            time.sleep(5)
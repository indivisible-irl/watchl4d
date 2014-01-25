import datetime
import os
import sys
import time
import redis
import rq_scheduler

from redis.exceptions import ConnectionError
# from redis import Redis
# from rq_scheduler.scheduler import Scheduler


# from util import print_with_timestamp, get_queue_name

def setup():
    dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, dir + '/../../')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'watchl4d.settings'

    # # This should be set by supervisord.conf
    # if 'DJANGO_LOCAL_ENV' not in os.environ:
    #     os.environ['DJANGO_LOCAL_ENV'] = os.environ['USER']

# def kill_jobs(scheduler, func_name):
#     for job in scheduler.get_jobs():
#         if func_name in job.data:
#             scheduler.cancel(job)

def run():
    from django.conf import settings
    from watchl4d.queue.scheduler import Scheduler

    connection = redis.Redis(
        settings.REDIS_HOST, 
        settings.REDIS_PORT, 
        settings.REDIS_DB, 
        settings.REDIS_PASSWORD)

    # Change the redis key prefixes that rq-scheduler uses
    # so that multiple schedulers can run on the same machine.
    # This only works because each scheduler is run as a different
    # python process in our environments
    # - rq_scheduler keeps track of
    # -- whether or not a scheduler is already running or not via 'scheduler_key'
    # -- keeps tracks of job schedules with 'scheduled_jobs_key'
    # Scheduler.scheduler_key += ':{0}'.format(os.environ['DJANGO_LOCAL_ENV'])
    # Scheduler.scheduled_jobs_key += ':{0}'.format(os.environ['DJANGO_LOCAL_ENV'])

    # Clear out the key rq-scheduler uses to know if scheduler is
    # already running because it takes a while for it to expire
    # and it gets in the way. (Be careful of starting up multiple schedulers however)
    connection.delete(rq_scheduler.Scheduler.scheduler_key)

    # Check for jobs every 10 seconds because thats how frequently we want our 
    # jobs to run as they are self-enqueueing.
    scheduler = rq_scheduler.Scheduler(
        # queue_name=get_queue_name(),
        connection=connection, 
        interval=10)


    Scheduler().schedule_set_streams()
    
    # import jobs.travelzoo
    # import jobs.expedia
    # kill_jobs(scheduler, 'jobs.travelzoo')
    # kill_jobs(scheduler, 'jobs.expedia')

    # We offset scheduled tasks by 5 minutes so that our redis worker
    # doesn't get hammered as soon as we start it.
    # I got sick of waiting for schecheduled jobs to complete before I'd
    # see the effects of other queued jobs (cache refreshes) during testing.
    # in_5_min = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # Create Real Deals from the Travelzoo RSS feed once every hour
    # scheduler.schedule(
    #     scheduled_time=in_5_min,
    #     func=jobs.travelzoo.create_realdeals,
    #     args=[],
    #     kwargs={},
    #     interval=3600,
    #     repeat=None)

    # # Create Real Deals from the Expedia API feed once every hour
    # scheduler.schedule(
    #     scheduled_time=in_5_min,
    #     func=jobs.expedia.create_realdeals,
    #     args=[],
    #     kwargs={},
    #     interval=3600,
    #     repeat=None)

    print 'Running'
    scheduler.run()

if __name__ == '__main__':
    setup()
    while True:
        try:
            run()
        except ConnectionError:
            print 'Unable to connect to redis! Trying to reconnect.'
            time.sleep(5)


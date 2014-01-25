import datetime
import redis
import rq_scheduler
from django.conf import settings

class Scheduler(object):
    def __init__(self):
        self.scheduler = rq_scheduler.Scheduler(connection=redis.Redis(
            settings.REDIS_HOST,
            settings.REDIS_PORT,
            settings.REDIS_DB,
            settings.REDIS_PASSWORD))

    def schedule_set_streams(self):
        print 'Enqueueing set_streams to run in 10 seconds.'
        import watchl4d.queue.jobs
        self.scheduler.enqueue_in(
            datetime.timedelta(seconds=10), 
            watchl4d.queue.jobs.set_streams)

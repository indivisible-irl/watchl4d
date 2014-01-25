import redis
import rq
from django.conf import settings

class Queue(object):
    def __init__(self):
        self.queue = rq.Queue(connection=redis.Redis(
            settings.REDIS_HOST,
            settings.REDIS_PORT,
            settings.REDIS_DB,
            settings.REDIS_PASSWORD))

    def set_streams(self, track_id):
        self.queue.enqueue_call(func='queue.jobs.set_streams', 
                                timeout=480) # 8 min
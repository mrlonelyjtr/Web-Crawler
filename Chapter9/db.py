from request import WeixinRequest
from redis import StrictRedis
from pickle import dumps, loads

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY = "weixin"

class RedisQueue(object):
    def __init__(self):
        self.db = StrictRedis(REDIS_HOST, REDIS_PORT)
    
    def add(self, request):
        if isinstance(request, WeixinRequest):
            return self.db.rpush(REDIS_KEY, dumps(request))

        return False

    def pop(self):
        if not self.empty():
            return loads(self.db.lpop(REDIS_KEY))
        else:
            return False
    
    def empty(self):
        return self.db.llen(REDIS_KEY) == 0

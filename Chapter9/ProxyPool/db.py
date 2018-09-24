import redis
from random import choice
from error import PoolEmptyError

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY = "proxies"

MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE = 10

class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT):
        self.db = redis.StrictRedis(host, port, decode_responses=True)
    
    def exists(self, proxy):
        return not self.db.zscore(REDIS_KEY, proxy) == None
    
    def add(self, proxy, score=INITIAL_SCORE):
        if not self.exists(proxy):
            self.db.zadd(REDIS_KEY, score, proxy)
    
    def decrease(self, proxy):
        score = self.db.zscore(REDIS_KEY, proxy)

        if score and score > MIN_SCORE:
            print("代理", proxy, "当前分数", score, "减1")
            self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print("代理", proxy, "当前分数", score, "移除")
            self.db.zrem(REDIS_KEY, proxy)
    
    def max(self, proxy):
        print("代理", proxy, "可用，设置为", MAX_SCORE)
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def random(self):
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)

        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)

            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError
    
    def count(self):
        return self.db.zcard(REDIS_KEY)

    def all(self):
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
from db import RedisClient
import aiohttp
import asyncio
import time
import sys

VALID_STATUS_CODES = [200]
TEST_URL = "http://www.baidu.com"
BATCH_TEST_SIZE = 100

class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    async def test_single_proxy(self, proxy):
        conn = aiohttp.TCPConnector(ssl=False)

        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf-8")
                
                real_proxy = "http://" + proxy
                print("正在测试", proxy)

                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print("代理可用", proxy)
                    else:
                        self.redis.decrease(proxy)
                        print("请求响应码不合法", proxy)
            except (aiohttp.ClientError, aiohttp.ClientConnectorError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print("代理请求失败", proxy)
    
    def run(self):
        print("测试器开始执行")
        try:
            proxies = self.redis.all()
            count = self.redis.count()
            loop = asyncio.get_event_loop()

            for i in range(0, count, BATCH_TEST_SIZE):
                test_proxies = proxies[i:i + BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print("测试器发生错误", e.args)
        finally:
            loop.close()

# 利用代理爬取微信公众号的文章，提取正文、发表日期、公众号等内容，然后把爬取结果保存到MySQL数据库。
import requests
from requests import Session
from requests import ReadTimeout, ConnectionError
from request import WeixinRequest
from db import RedisQueue
from urllib.parse import urlencode
from mysql import MySQL
from pyquery import PyQuery as pq
import re
import sys

PROXY_POOL_URL = "http://127.0.0.1:5000/random"
VALID_STATUSES = [200]
MAX_FAILED_TIME = 50

class Wechat(object):
    base_url = "http://weixin.sogou.com/weixin"
    keyword = "nba"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
        "Cookie": 'sct=2; ppmdig=153798156900000029b2c90dd10104a88b02afad382cf017; ppinf=5|1537799457|1539009057|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxMTptcmxvbmVseWp0cnxjcnQ6MTA6MTUzNzc5OTQ1N3xyZWZuaWNrOjExOm1ybG9uZWx5anRyfHVzZXJpZDo0NDpvOXQybHVGUEpyZHBxQ0dWR09VdG4xb1ZveU5nQHdlaXhpbi5zb2h1LmNvbXw; pprdig=YrgiDGJBorgcLoekzZXOYzQGDDiQ1I06___HgQ82ouWk1pkxaD2ON7U0nMVTZ7cKn6QkbWSGMo2frdWi81FXGx76xMXLPID5wg-hMXm2x9GKImc75S2POjyaM1ybQGA8ICZmUgUcOJt2hIfQCPulkQjE2rGEOPp6zbBzPCvXinE; sgid=02-35144799-AVuo9SEdkhQRYFdDtzBL72k; SNUID=3A94A629F3F6856D4D4A75AAF413208B; JSESSIONID=aaadNfym5dl1OgUejcHvw; SUV=006425A0DA5267C95BA8F38BC42D4423; IPLOC=CN3100; SUID=C96752DA2C12960A000000005BA8F38A; SUID=C96752DA3F18960A000000005BA8F389; ABTEST=0|1537799049|v1; weixinIndexVisited=1',
        "Host": 'weixin.sogou.com',
        "Upgrade-Insecure-Requests": 1,
        "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        "Accept-Encoding": 'gzip, deflate',
        "Accept-Language": 'zh-CN,zh;q=0.9',
        "Cache-Control": 'no-cache',
        "Connection": 'keep-alive'
    }

    session = Session()
    queue = RedisQueue()
    mysql = MySQL()

    def get_proxy(self):
        try:
            response = requests.get(PROXY_POOL_URL)

            if response.status_code == 200:
                print("Get Proxy", response.text)
                return response.text
            return None
        except ConnectionError:
            return None

    def start(self):
        self.session.headers.update(self.headers)
        start_url = self.base_url + "?" + urlencode({"query": self.keyword, "type": 2})
        weixin_request = WeixinRequest(url=start_url, callback=self.parse_index, need_proxy=True)
        self.queue.add(weixin_request)
    
    def schedule(self):
        while not self.queue.empty():
            weixin_request = self.queue.pop()
            callback = weixin_request.callback
            print("Schedule", weixin_request.url)
            response = self.request(weixin_request)

            if response and response.status_code in VALID_STATUSES:
                results = list(callback(response))

                if results:
                    for result in results:
                        print("New Result", type(result))

                        if isinstance(result, WeixinRequest):
                            self.queue.add(result)
                        if isinstance(result, dict):
                            self.mysql.insert("articles", result)
                else:
                    self.error(weixin_request)
            else:
                self.error(weixin_request)

            sys.stdout.flush()
    
    def request(self, weixin_request):
        try:
            if weixin_request.need_proxy:
                proxy = self.get_proxy()

                if proxy:
                    proxies = {
                        "http": "http://" + proxy,
                        "https": "https://" + proxy
                    }
                    return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout, proxies=proxies)
            return self.session.send(weixin_request.prepare(), timeout=weixin_request.timeout)
        except (ConnectionError, ReadTimeout) as e:
            print(e.args)
            return False
    
    def parse_index(self, response):
        doc = pq(response.text)
        items = doc(".news-list .txt-box h3 a").items()

        for item in items:
            url = item.attr("href")
            yield WeixinRequest(url=url, callback=self.parse_detail)
        
        page = doc("#sogou_next").attr("href")

        if page:
            url = self.base_url + str(page)
            yield WeixinRequest(url=url, callback=self.parse_index, need_proxy=True)

    def parse_detail(self, response):
        doc = pq(response.text)
        yield {
            'title': doc('.rich_media_title').text(),
            'content': doc('.rich_media_content').text(),
            'date': re.search('publish_time = "(.*?)"', response.text).group(1),
            'nickname': doc('#js_profile_qrcode > div > strong').text(),
            'wechat': doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        }
    
    def error(self, weixin_request):
        weixin_request.fail_time = weixin_request.fail_time + 1
        print('Request Failed', weixin_request.fail_time, 'Times', weixin_request.url)
        
        if weixin_request.fail_time < MAX_FAILED_TIME:
            self.queue.add(weixin_request)
    
    def run(self):
        self.start()
        self.schedule()

if __name__ == "__main__":
    wechat = Wechat()
    wechat.run()

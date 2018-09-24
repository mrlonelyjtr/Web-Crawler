import requests
from requests.exceptions import ConnectionError
import time

base_headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15"
}

def get_page(url, options={}):
    headers = dict(base_headers, **options)
    print('正在抓取', url)

    try:
        time.sleep(1)
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print('抓取成功', url, response.status_code)
            return response.text
    except ConnectionError:
        print('抓取失败', url)
        return None

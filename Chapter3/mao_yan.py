# 提取出猫眼电影TOP100的电影名称、时间、评分、图片等信息，提取的结果会以文件形式保存下来。
import requests
import re
from requests.exceptions import RequestException
import json
import time

def get_one_page(url, offset):
    try:
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15"
        }
        params = {
            'offset': offset
        }
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    regex = '<dd>.*?board-index.*?>(.*?)</i>.*?data-src="(.*?)".*?name.*?a.*?>(.*?)</a>.*?star.*?>(.*?)</p>.*?releasetime.*?>(.*?)</p>.*?integer.*?>(.*?)</i>.*?fraction.*?>(.*?)</i>.*?</dd>'
    pattern = re.compile(regex, re.S)
    items = re.findall(pattern, html)
    
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2].strip(),
            'actor': item[3].strip()[3:] if len(item[3]) > 3 else "",
            'time': item[4].strip()[5:] if len(item[4]) > 5 else "",
            'score': item[5].strip() + item[6].strip()
        }

def write_to_file(content):
    with open('result.txt', 'a') as f:
        f.write(json.dumps(content, ensure_ascii=False) + "\n")

def main(offset):
    url = "http://maoyan.com/board/4"
    html = get_one_page(url, offset)
    for item in parse_one_page(html):  
        #print(item)
        write_to_file(item)

if __name__ == '__main__':
    for i in range(10):
        main(offset=i * 10)
        time.sleep(1)
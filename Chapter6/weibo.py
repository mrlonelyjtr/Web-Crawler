# 用Python来模拟Ajax请求，把发过的前10页微博全部爬取下来。
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient

client = MongoClient()
db = client.weibo
collection = db.weibo

def get_page(page):
    url = "https://m.weibo.cn/api/container/getIndex?"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
        'Referer': 'https://m.weibo.cn/u/2830678474',
        'X-Requested-With': 'XMLHttpRequest'
    }
    params = {
        'type': 'uid',
        'value': 2830678474,
        'containerid': 1076032830678474,
        'page': page
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print("Error", e.args)

def parse_page(json):
    items = json.get("data").get("cards")
    
    for item in items: 
        item = item.get("mblog")
        if item:
            yield {
                'id': item.get("id"),
                'text': pq(item.get("text")).text(),
                'attitudes': item.get("attitudes_count"),
                'comments': item.get("comments_count"),
                'reposts': item.get("reposts_count")
            }

def save_to_mongo(result):
    collection.insert_one(result)

if __name__ == '__main__':
    for page in range(1, 11):
        json = get_page(page)
        results = parse_page(json)

        for result in results:
            #print(result)
            save_to_mongo(result)

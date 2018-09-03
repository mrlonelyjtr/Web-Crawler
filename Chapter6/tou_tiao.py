# 抓取今日头条的街拍美图，将每组图片分文件夹下载到本地并保存下来。
import requests
from pyquery import PyQuery as pq
import os
from hashlib import md5
from multiprocessing.pool import Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_page(offset):
    url = "https://www.toutiao.com/search_content/?"
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        'from': 'search_tab'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        return None

def get_images(json):
    items = json.get("data")

    for item in items:
        title = item.get("title")
        images = item.get("image_list")
        if title and images:
            for image in images:
                yield {
                    'title': title,
                    'image': "https:" + image.get("url")
                }

def save_images(item):
    dir_path = "img/{0}".format(item.get("title"))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    try:
        response = requests.get(item.get("image"), headers=headers)
        if response.status_code == 200:
            file_path = "{0}/{1}.{2}".format(dir_path, md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print("Already Downloaded", file_path)
    except requests.ConnectionError:
        print("Failed to Save Image")

def main(offset):
    json = get_page(offset)
    
    for item in get_images(json):
        #print(item)
        save_images(item)

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(0, 21)])
    pool.map(main, groups)
    pool.close()
    pool.join()
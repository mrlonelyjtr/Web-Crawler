# 利用Selenium抓取淘宝商品并用pyquery解析得到商品的图片、名称、价格、购买人数、店铺名称和店铺所在地信息，并将其保存到MongoDB。
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq
from pymongo import MongoClient

KEY_WORD = 'iPad'
MAX_PAGE = 100

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 10)

client = MongoClient()
db = client.taobao
collection = db.products

def index_page(page):
    print("正在爬取第", page, "页")
    try:
        url = "https://s.taobao.com/search?q=" + quote(KEY_WORD)
        browser.get(url)

        if page > 1:
            input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#mainsrp-pager div.form > input")))
            submit = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#mainsrp-pager div.form > span.btn")))
            input.clear()
            input.send_keys(page)
            submit.click()

        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, "#mainsrp-pager li.active > span"), str(page)))
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".m-itemlist .items .item")))
        
        get_products()

    except TimeoutException:
        index_page(page)

def get_products():
    doc = pq(browser.page_source)
    items = doc("#mainsrp-itemlist .items .item").items()

    for item in items:
        product = {
            'image': item.find(".pic .img").attr("data-src"),
            'price': item.find(".price").text().replace("\n", " "),
            'deal': item.find(".deal-cnt").text(),
            'title': item.find(".title").text().replace("\n", " "),
            'shop': item.find(".shop").text(),
            'location': item.find(".location").text()
        }

        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        collection.insert_one(result)
        print("存储到MongoDB成功")
    except Exception:
        print("存储到MongoDB失败")

def main():
    for page in range(1, MAX_PAGE + 1):
        index_page(page)

    browser.close()

if __name__ == '__main__':
    main()
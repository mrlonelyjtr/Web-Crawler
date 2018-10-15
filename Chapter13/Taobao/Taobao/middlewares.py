# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from logging import getLogger
from scrapy.http import HtmlResponse

class SeleniumMiddleware(object):
    def __init__(self, timeout=None):
        self.logger = getLogger(__name__)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.set_window_size(1400, 700)
        self.browser.set_page_load_timeout(timeout)
        self.wait = WebDriverWait(self.browser, timeout)
    
    def __del__(self):
        self.browser.close()
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            timeout = crawler.settings.get("SELENIUM_TIMEOUT")
        )
    
    def process_request(self, request, spider):
        self.logger.debug("ChromeDriver is Starting")
        page = request.meta.get("page", 1)

        try:
            self.browser.get(request.url)

            if page > 1:
                input = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#mainsrp-pager div.form > input")))
                submit = self.wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#mainsrp-pager div.form > span.btn")))
                input.clear()
                input.send_keys(page)
                submit.click()

            self.wait.until(EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, "#mainsrp-pager li.active > span"), str(page)))
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".m-itemlist .items .item")))
            return HtmlResponse(url=request.url, status=200, request=request, body=self.browser.page_source, encoding='utf-8')

        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

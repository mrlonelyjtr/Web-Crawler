from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO
from chaojiying import Chaojiying_Client
import random

USERNAME = "mrlonelyjtr"
PASSWORD = ""
SOFTID = 897262
KIND = 9004

class CrackGeeTest():
    def __init__(self):
        self.url = "http://www.geetest.com/type/"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.chaojiying = Chaojiying_Client(USERNAME, PASSWORD, SOFTID)

    def __del__(self):
        self.browser.close()

    def open(self):
        self.browser.get(self.url)
        behavior = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".products-content li:nth-of-type(3)")))
        time.sleep(2)
        behavior.click()

    def get_geetest_button(self):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_radar_tip")))

    def get_geetest_image(self, name):
        top, bottom, left, right, size = self.get_position()
        #print("验证码位置", top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left * 2, top * 1.5, right * 2, bottom * 1.65))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        return captcha

    def get_position(self):
        img = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "geetest_widget")))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location["y"], location["y"] + size["height"], location["x"], location["x"] + size["width"]
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))
    
    def get_points(self, captcha_result):
        groups = captcha_result.get("pic_str").split("|")
        locations = [[int(number) for number in group.split(",")] for group in groups]
        return locations

    def touch_click_words(self, locations):
        img = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "geetest_widget")))

        for location in locations:
            #print(location)
            ActionChains(self.browser).move_to_element_with_offset(img, location[0], location[1]).click().perform()
            time.sleep(1)
    
    def touch_click_verify(self):
        confirm = self.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "geetest_commit")))
        confirm.click()

    def crack(self):
        self.open()
        button = self.get_geetest_button()
        button.click()
        image = self.get_geetest_image("captcha.png")
        byte_array = BytesIO()
        image.save(byte_array, format='PNG')
        result = self.chaojiying.post_pic(byte_array.getvalue(), KIND)
        print(result)

        if result.get("err_no") == 0:
            locations = self.get_points(result)
            self.touch_click_words(locations)
            self.touch_click_verify()
            time.sleep(1)

            try:
                self.wait.until(EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "geetest_success_radar_tip_content"), "验证成功"))
                print("SUCCESS")
            except Exception:
                self.crack()
        else:
            self.chaojiying.report_error(result.get("pic_id"))

if __name__ == "__main__":
    crack = CrackGeeTest()
    crack.crack()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO

THRESHOLD = 60
LEFT = 60
BORDER = 6

class CrackGeeTest():
    def __init__(self):
        self.url = "http://www.geetest.com/type/"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)

    def __del__(self):
        self.browser.close()

    def open(self):
        self.browser.get(self.url)
        behavior = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".products-content li:nth-of-type(2)")))
        time.sleep(2)
        behavior.click()

    def get_geetest_button(self):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_radar_tip")))

    def get_geetest_image(self, name, full):
        top, bottom, left, right, size = self.get_position(full)
        #print("验证码位置", top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left * 2, top * 1.59, right * 2, bottom * 1.73))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        #captcha.save(name)
        return captcha

    def get_position(self, full):
        img = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "geetest_canvas_img")))
        fullbg = self.wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "geetest_canvas_fullbg")))
        time.sleep(2)

        if full:
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])", fullbg, "style", "")
        else:
            self.browser.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])", fullbg, "style", "display: none")

        location = img.location
        size = img.size
        top, bottom, left, right = location["y"], location["y"] + \
            size["height"], location["x"], location["x"] + size["width"]
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def get_gap(self, image1, image2):
        for i in range(LEFT, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    return i
        return LEFT

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if abs(pixel1[0] - pixel2[0]) < THRESHOLD and abs(pixel1[1] - pixel2[1]) < THRESHOLD and abs(pixel1[2] - pixel2[2]) < THRESHOLD:
            return True
        else:
            return False

    def get_track(self, distance):
        distance += 20
        forward_tracks = []
        mid = distance * 4 / 5
        current = 0
        t = 0.2
        v = 0

        while current < distance:
            if current < mid:
                a = 2
            else:
                a = -3

            v0 = v
            v = v0 + a * t
            x = v0 * t + 0.5 * a * t * t
            current += x
            forward_tracks.append(round(x))

        backward_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
        return {'forward_tracks': forward_tracks, 'backward_tracks': backward_tracks}

    def get_slider(self):
        return self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "geetest_slider_button")))

    def move_to_gap(self, slider, track):
        ActionChains(self.browser).click_and_hold(slider).perform()

        for x in track['forward_tracks']:
            ActionChains(self.browser).move_by_offset(
                xoffset=x, yoffset=0).perform()

        time.sleep(0.5)

        for x in track['backward_tracks']:
            ActionChains(self.browser).move_by_offset(
                xoffset=x, yoffset=0).perform()

        ActionChains(self.browser).release().perform()

    def crack(self):
        self.open()
        button = self.get_geetest_button()
        button.click()
        image1 = self.get_geetest_image("captcha1.png", True)
        image2 = self.get_geetest_image("captcha2.png", False)
        gap = self.get_gap(image1, image2)
        #print("缺口位置", gap)
        track = self.get_track(gap - BORDER)
        #print("滑动轨迹", track)
        slider = self.get_slider()
        self.move_to_gap(slider, track)
        time.sleep(1)

        try:
            self.wait.until(EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "geetest_success_radar_tip_content"), "验证成功"))
            print("SUCCESS")
        except Exception:
            self.crack()

if __name__ == "__main__":
    crack = CrackGeeTest()
    crack.crack()

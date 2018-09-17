from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import time
from PIL import Image
from io import BytesIO
from os import listdir

TEMPLATES_FOLDER = 'templates/'
THRESHOLD_IMAGE = 0.99
THRESHOLD_PIXEL = 20
TIMES = 30

class CrackWeiboSlide():
    def __init__(self):
        self.url = "https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/"
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = ""
        self.password = ""

    def __del__(self):
        self.browser.close()

    def open(self):
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, "loginName")))
        password = self.wait.until(EC.presence_of_element_located((By.ID, "loginPassword")))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, "loginAction")))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()

    def get_image(self, name):
        top, bottom, left, right, size = self.get_position()
        #print("验证码位置", top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left * 2, top * 2, right * 2, bottom * 2))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        #captcha.save(name)
        return captcha

    def get_position(self):
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "patt-shadow")))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location["y"], location["y"] + size["height"], location["x"], location["x"] + size["width"]
        return (top, bottom, left, right, size)

    def get_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))
    
    def detect_image(self, image):
        for template_name in listdir(TEMPLATES_FOLDER):
            print("正在匹配", template_name)
            template = Image.open(TEMPLATES_FOLDER + template_name)

            if self.same_image(image, template):
                numbers = [int(number) for number in list(template_name.split(".")[0])]
                print("拖动顺序", numbers)
                return numbers
    
    def same_image(self, image, template):
        count = 0

        for x in range(image.width):
            for y in range(image.height):
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        
        result = float(count) / (image.width * image.height)
        if result > THRESHOLD_IMAGE:
            print("成功匹配")
            return True
        else:
            return False
    
    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if abs(pixel1[0] - pixel2[0]) < THRESHOLD_PIXEL and abs(pixel1[1] - pixel2[1]) < THRESHOLD_PIXEL and abs(pixel1[2] - pixel2[2]) < THRESHOLD_PIXEL:
            return True
        else:
            return False
    
    def move(self, numbers):
        circles = self.browser.find_elements_by_css_selector(".patt-circ")
        dx = dy = 0

        for i in range(4):
            circle = circles[numbers[i]-1]
            x = circle.size["width"] / 2
            y = circle.size["height"] / 2

            if i == 0:
                ActionChains(self.browser).move_to_element_with_offset(circle, x, y).click_and_hold().perform()
            else:
                for t in range(TIMES):
                    ActionChains(self.browser).move_by_offset(dx / TIMES, dy / TIMES).perform()
                    time.sleep(1 / TIMES)
            
            if i == 3:
                ActionChains(self.browser).release().perform()
            else:
                dx = circles[numbers[i+1]-1].location["x"] - circle.location["x"]
                dy = circles[numbers[i+1]-1].location["y"] - circle.location["y"]

    def crack(self):
        self.open()
        image = self.get_image("captcha.png")
        numbers = self.detect_image(image)
        self.move(numbers)
        time.sleep(5)
        print("识别结束")

    def main(self):
        count = 0
        
        while count < 100:
            try:
                self.open()
                self.get_image(str(count) + ".png")
                count += 1
            except TimeoutException:
                print('未出现验证码')

if __name__ == "__main__":
    crack = CrackWeiboSlide()
    #crack.main()
    crack.crack()

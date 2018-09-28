# 模拟登录，同时爬取登录后才可以访问的页面信息，如好友动态、个人信息等内容。
import requests
from lxml import etree

class Login(object):
    def __init__(self):
        self.login_url = "https://github.com/login"
        self.post_url = "https://github.com/session"
        self.dynamics_url = "https://github.com/dashboard-feed"
        self.profile_url = "https://github.com/settings/profile"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15'
        }
        self.session = requests.Session()
    
    def login(self, username, password):
        post_data = {
            "commit": "Sign in",
            "utf8": "✓",
            "authenticity_token": self.token(),
            "login": username,
            "password": password
        }
        
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        
        if response.status_code == 200:
            response = self.session.get(self.dynamics_url, headers=self.headers)
            self.dynamics(response.text)
        
        response = self.session.get(self.profile_url, headers=self.headers)

        if response.status_code == 200:
            self.profile(response.text)
    
    def token(self):
        response = self.session.get(self.login_url, headers=self.headers)
        selector = etree.HTML(response.text)
        return selector.xpath("//input[@name='authenticity_token']/@value")
    
    def dynamics(self, html):
        selector = etree.HTML(html)
        dynamics = selector.xpath("//div[contains(@class, 'py-3')]")
        for dynamic in dynamics:
            item = dynamic.xpath(".//div[contains(@class, 'flex-items-baseline')]")[0].xpath('normalize-space(string(.))')
            print(item)
            
    def profile(self, html):
        selector = etree.HTML(html)
        name = selector.xpath("//input[@id='user_profile_name']/@value")[0]
        email = selector.xpath("//select[@id='user_profile_email']/option[@value!='']/text()")
        print(name, email)

if __name__ == "__main__":
    login = Login()
    login.login(username='mrlonelyjtr', password='')

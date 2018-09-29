# 爬取去哪儿网的旅游攻略，将所有攻略的作者、标题、出发日期、人均费用、攻略正文等保存下来。
from pyspider.libs.base_handler import *

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://travel.qunar.com/travelbook/list.htm',
                   callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('li > .tit > a').items():
            self.crawl(each.attr.href, callback=self.detail_page,
                       fetch_type='js')

        next = response.doc('.next').attr.href
        self.crawl(next, callback=self.index_page)

    @config(priority=2)
    def detail_page(self, response):
        return {
            "url": response.url,
            "title": response.doc('#booktitle').text(),
            'date': response.doc('.when .data').text(),
            'day': response.doc('.howlong .data').text(),
            'who': response.doc('.who .data').text(),
            'text': response.doc('#b_panel_schedule').text(),
            'image': response.doc('.cover_img').attr.src
        }

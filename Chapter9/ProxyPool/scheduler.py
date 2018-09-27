from getter import Getter
from tester import Tester
from api import app
from multiprocessing import Process
import time

TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True
TESTER_CYCLE = 20
GETTER_CYCLE = 20
API_HOST = "0.0.0.0"
API_PORT = 5000

class Scheduler(object):
    def schedule_getter(self, cycle=GETTER_CYCLE):
        getter = Getter()
        while True:
            print("开始抓取代理")
            getter.run()
            time.sleep(cycle)

    def schedule_tester(self, cycle=TESTER_CYCLE):
        tester = Tester()
        while True:
            print("测试器开始运行")
            tester.run()
            time.sleep(cycle)

    def schedule_api(self):
        app.run(API_HOST, API_PORT)
    
    def run(self):
        print("代理池开始运行")
        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()
        
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()
        
        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()

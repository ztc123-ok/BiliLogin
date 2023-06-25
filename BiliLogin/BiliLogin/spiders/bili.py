import scrapy
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import time
from lxml import etree
import requests
import re
from time import sleep
from get_user_agent import get_user_agent_of_pc
from selenium.webdriver.chrome.service import Service
import requests
from PIL import Image
from chaojiying import Chaojiying_Client
from selenium.webdriver.support import expected_conditions as EC

class BiliSpider(scrapy.Spider):
    name = "bili"
    allowed_domains = ["bilibili.com"]
    start_urls = ["https://passport.bilibili.com/login"]

    def parse(self, response):#返回json,none,item,request
        self.login()
        #self.recognize()
        self.get_img()
        self.click_chain()


    def __init__(self):
        chrome_driver = "C:/Users/周/Desktop/selenium_example/chromedriver_win32/chromedriver.exe"
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")
        options.add_argument("disable-infobars")
        options.add_argument("user-agent=" + get_user_agent_of_pc())
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        s = Service(executable_path=chrome_driver)
        self.chrome = webdriver.Chrome(options=options, service=s)
        self.chrome.maximize_window()

    def spider_close(self):
        self.chrome.quit()

    def get_img(self):
        img_url = self.chrome.find_element(by=By.XPATH,value='//div[@class="geetest_item_wrap"]').get_attribute('style')
        print("抽取图片：",img_url)
        img_url = img_url.split("(\"")[1].split("\")")[0]
        print("img_url:",img_url)
        headers = {
            "User-Agent":get_user_agent_of_pc()
        }

        session = requests.Session()
        img_data = session.get(url = img_url,headers=headers).content
        with open('D:/爬取数据/bibibi_img.jpg','wb') as f:
            f.write(img_data)

        img1 = Image.open('D:/爬取数据/bibibi_img.jpg')
        #img2 = img1.resize((259,290))
        img2 = img1.resize((307, 343))
        img2.save('D:/爬取数据/bibibi_img2.jpg')

    #使用第三方 超级鹰 辅助获取位置信息
    def recognize(self):
        pic = open('D:/爬取数据/bibibi_img2.jpg','rb').read()
        chaojiying = Chaojiying_Client('119','119','945566')
        yzm_coordinates =chaojiying.PostPic(pic,9004)['pic_str']
        words = chaojiying.PostPic(pic,2004)['pic_str']
        word_dict = {}

        print('识别的汉字的坐标：',yzm_coordinates)
        print('识别的汉字',words)
        return yzm_coordinates,words

    def login(self):
        username = "119"
        pwd ="119"
        WebDriverWait(self.chrome,timeout=5).until(EC.presence_of_element_located((By.XPATH,'//input[@placeholder="请输入账号"]'))).send_keys(username)
        WebDriverWait(self.chrome, timeout=5).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请输入密码"]'))).send_keys(pwd)
        WebDriverWait(self.chrome, timeout=5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]'))).click()
        time.sleep(2 + random.random())#等图片出现

    def click_chain(self):
        yzms,words = self.recognize()
        all_list = []#存储即将被点击汉字的坐标
        words_dict = {}
        # 150,98| 45,83 | 55,55
        if '|'in yzms:
            splits = yzms.split('|')
            for i in range(len(splits)):
                xy_list = []
                x = int(splits[i].split(',')[0]) + 6#根据实际情况调整
                y = int(splits[i].split(',')[1]) + 8#根据实际情况调整
                xy_list.append(x)
                xy_list.append(y)
                if len(words)==len(splits):#有的文字识别不出来但有坐标
                    words_dict[words[i]]=(x,y)
                all_list.append(xy_list)
        else :#只有一个汉字
            xy_list = []
            x = int(yzms.split(',')[0])+6
            y = int(yzms.split(',')[1])+8
            xy_list.append(x)
            xy_list.append(y)
            if len(words)>0:
                words_dict[words] = (x, y)
            all_list.append(xy_list)

        print('all_list=',all_list)
        print('words_dic=',words_dict)

        for l in all_list:
            img_element = self.chrome.find_element(by=By.XPATH,value='//div[@class="geetest_item_wrap"]/img')
            code_tag_half_width = float(img_element.rect['width']) / 2
            code_tag_half_height = float(img_element.rect['height']) / 2
            print("code_tag_half_width",code_tag_half_width,"code_tag_half_height",code_tag_half_height)
            ActionChains(self.chrome).move_to_element_with_offset(img_element,l[0]-code_tag_half_width,l[1]-code_tag_half_height).click().pause(0.1+random.random()).perform()
            #版本高了按中心为原点
            time.sleep(1+random.random())
        time.sleep(2 + random.random())
        ActionChains(self.chrome).click(self.chrome.find_element(by=By.XPATH,value='/html/body/div[4]/div[2]/div[6]/div/div/div[3]/a/div')).perform()#确认
        print("点击成功")



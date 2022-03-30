import time
import os.path
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import config

class VCNewsParser:
    last_post = ""
    driver = None

    # number of page scrolling 
    page_downs_num=15

    def __init__(self):
        # use chrome driver for scrolling page
        self.driver = webdriver.Chrome(executable_path=config.chromedriver_path)
        self.driver.get(config.url)
        time.sleep(1)

    def set_last_post(self, last_post):
        self.last_post = last_post

    def new_posts(self):
        self.driver.refresh()
        elem = self.driver.find_element(by=By.TAG_NAME, value="body")

        # function for getting post's hrefs, if structure of site will change -> need change this function
        get_posts_urls = lambda driver: list(map(lambda x: x.get_attribute("href"), self.driver.find_elements(by=By.CLASS_NAME, value="content-link")))

        posts = get_posts_urls(self.driver)

        scroll_count = 0
        # if post didnt find in current posts -> scroll page down and search again 10 times
        while self.last_post not in posts and scroll_count < 10:
            for i in range(self.page_downs_num):
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)
            posts = get_posts_urls(self.driver)
            scroll_count += 1
        
        # if post didnt find -> return last post from page
        if scroll_count == 10:
            return [self.driver.find_element(by=By.CLASS_NAME, value="content-link").get_attribute("href")]

        #cut last posts
        posts = posts[0:posts.index(self.last_post)]
        # reverse
        return posts[::-1]

    def post_info(self, link):
        r = requests.get(link)
        html = BS(r.content, 'html.parser')
        info = {}
        try:
            # get photo url
            # if code of webpage is change -> need to change this block
            try:
                img_url = html.find("div","content").find("div", "andropov_image")["data-image-src"]
            except:
                img_url = None 

            # get info about post
            # if code of webpage is change -> need to change this block
            info = {
                "category" : "#" + html.find("div", "content-header-author__name").text[17: -12].replace(" ", "_"),
                "title": html.find("h1", "content-title").text[21:].replace("Статьи редакции",'').replace('\n', '').replace("  ", ""),
                "description": html.find("div", "content content--full").find("p").text,
                "link": link,
                "img_url": img_url
            }
        except: 
            print("Something went wrong")
        r.close()
        return info

    def download_image(self, url):
        # cut last /
        url = url[:-1]
        r = requests.get(url, allow_redirects=True)

        a = urlparse(url)
        filename = os.path.basename(a.path)
        # save header image to local disk
        open(filename, 'wb').write(r.content)

        return filename
    
    def delete_image(self, filename):
        os.remove(filename)
        
    def close_all_sessions(self):
        self.driver.quit()
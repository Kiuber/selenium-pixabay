# -*- coding: utf-8 -*-

import re
import shutil
from cpbox.app.devops import DevOpsApp
from cpbox.tool import http
from cpbox.tool import file
from cpbox.tool import functocli

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

APP_NAME = 'selenium-pixabay'
URL = 'https://pixabay.com/'

class App(DevOpsApp):
    def __init__(self, **kwargs):
        DevOpsApp.__init__(self, APP_NAME, **kwargs)
        self.imgs_dir = self.app_runtime_storage_dir + '/imgs'
        file.ensure_dir(self.imgs_dir)

    def detect_and_download(self):
        with webdriver.Chrome() as driver:
            try:
                chrome_options = Options()
                # chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('blink-settings=imagesEnabled=false')
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("window-size=1400,600")
                chrome_options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(chrome_options=chrome_options)
                driver.get(URL)
                item_element_list = driver.find_elements_by_class_name('item')
                for item_element in item_element_list:
                    img_element = item_element.find_element_by_tag_name('img')
                    mess_img_url_str = self._get_mess_img_url_str(img_element)
                    img_url_list = re.findall('(https?:[/|.|\w|\s|-]*\.(?:jpg|gif|png))', mess_img_url_str)
                    img_url = img_url_list[-1]

                    a_element = img_element.find_element_by_xpath('..')
                    href_str = a_element.get_attribute('href')
                    img_suffix = img_url.split('/')[-1].split('.')[-1]
                    local_img_file_name = ('%s.%s') % (href_str.split('/')[-2], img_suffix)
                    local_img_file_name = ('%s/%s') % (self.imgs_dir, local_img_file_name)

                    self._download_img(img_url, local_img_file_name)
                    print('downloaded to %s' % local_img_file_name)
                driver.quit()
            except:
                driver.quit()

    def _get_mess_img_url_str(self, element):
        str = element.get_attribute('srcset')
        if str == '':
            str = element.get_attribute('data-lazy-srcset')
        return str

    def _download_img(self, img_url, local_img_file_name):
        local_img_file = open(local_img_file_name, 'wb')
        respone = http.get(img_url, stream=True)
        shutil.copyfileobj(respone.raw, local_img_file)

if __name__ == '__main__':
    functocli.run_app(App)

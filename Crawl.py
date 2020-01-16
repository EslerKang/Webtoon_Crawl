# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from img2pdf import convert
import time
import shutil


# pdf 파일들 이름 오름차순 정렬 시 키 값
def convert_digit(s):
    s = s.split('.')
    s = s[0]
    return int(s)


# 메인 크롤기능
def crawl_webtoon(episode_url):

    key_path = "../key.txt"
    key_file = open(key_path)
    key_content = key_file.read()
    key_component = key_content.split(' ')
    ID = key_component[0]
    PWD = key_component[1]

    print("Key value imported")

    driver_path = '../chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('lang=ko_KR')
    driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)
    driver.get('https://nid.naver.com/nidlogin.login')

    print("Going to Login Page")

    driver.execute_script("document.getElementsByName('id')[0].value=\'" + ID + "\'")
    driver.execute_script("document.getElementsByName('pw')[0].value=\'" + PWD + "\'")
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

    print("Login success!")

    driver.implicitly_wait(30)
    time.sleep(2.5)

    for url in episode_url:

        driver.get(url)
        # time.sleep(10)
        try:
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR,"img[src='https://static-comic.pstatic.net/staticImages/COMICWEB/NAVER/img/common/blank.gif']")))
        except Exception as ex:
            print("Page Loading Error")
            print(ex)

        print("Loaded Webtoon Page!")

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        print('Parse success')

        comic_title = ' '.join(soup.select('.comicinfo h2')[0].text.split())
        ep_title = ' '.join(soup.select('.tit_area h3')[0].text.split())
        if ep_title+".pdf" in os.listdir(os.path.join(os.path.dirname(__file__), comic_title)):
            print(ep_title+" Already Exist")
            continue

        image_name_list = []
        for img_tag in soup.select('.wt_viewer img'):
            image_file_url = img_tag['src']
            image_dir_path = os.path.join(os.path.dirname(__file__), comic_title, ep_title+"_img")
            image_name = os.path.basename(image_file_url)
            image_name_splited = image_name.split('_')
            image_file_path = os.path.join(image_dir_path, image_name_splited[len(image_name_splited)-1])
            image_name_list.append(image_name_splited[len(image_name_splited)-1])

            if not os.path.exists(image_dir_path):
                os.makedirs(image_dir_path)

            print(image_file_path)

            headers = {'Referer': url}
            image_file_data = requests.get(image_file_url, headers=headers).content

            open(image_file_path, 'wb').write(image_file_data)

        print('Completed to download!')

        os.chdir(image_dir_path)

        with open(ep_title+".pdf", "wb") as f:
            f.write(convert([i for i in image_name_list if i.endswith('.jpg')]))
            f.close()
        os.chdir("../")
        shutil.move(image_dir_path+"/"+ep_title+".pdf", ep_title+".pdf")

        shutil.rmtree(image_dir_path)
        os.chdir("../")

        print("Merge complete!\n")

    driver.quit()

    print("Complete!")


if __name__ == '__main__':
    episode_url = []
    webtoon = {
        '670143': 208
    }
    for i in webtoon.keys():
        for j in range(206, webtoon[i]+1):
            episode_url.append('https://comic.naver.com/webtoon/detail.nhn?titleId='+i+'&no='+str(j))
    crawl_webtoon(episode_url)

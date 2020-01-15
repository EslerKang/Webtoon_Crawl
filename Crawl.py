# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
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
    ID = key_component[1]
    PWD = key_component[3]

    print("Key value imported")

    driver_path = '../chromedriver'
    driver = webdriver.Chrome(driver_path)
    driver.get('https://nid.naver.com/nidlogin.login')

    print("Going to Login Page")

    driver.execute_script("document.getElementsByName('id')[0].value=\'" + ID + "\'")
    driver.execute_script("document.getElementsByName('pw')[0].value=\'" + PWD + "\'")
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

    print("Login success!")

    driver.implicitly_wait(15)
    time.sleep(2.5)

    driver.get(episode_url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    print('Parse success')

    comic_title = ' '.join(soup.select('.comicinfo h2')[0].text.split())
    ep_title = ' '.join(soup.select('.tit_area h3')[0].text.split())

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

        headers = {'Referer': episode_url}
        image_file_data = requests.get(image_file_url, headers=headers).content

        open(image_file_path, 'wb').write(image_file_data)

    print('Completed to download!')
    driver.quit()

    os.chdir(image_dir_path)

    with open(ep_title+".pdf", "wb") as f:
        f.write(convert([i for i in image_name_list if i.endswith('.jpg')]))
        f.close()
    os.chdir("../")
    shutil.move(image_dir_path+"/"+ep_title+".pdf", ep_title+".pdf")
    
    shutil.rmtree(image_dir_path)
    os.chdir("../")

    print("Merge complete!")


if __name__ == '__main__':
    for i in range(1, 209):
        episode_url = 'https://comic.naver.com/webtoon/detail.nhn?titleId='+'670143'+'&no='+str(i)
        crawl_webtoon(episode_url)

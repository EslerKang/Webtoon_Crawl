# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image


def convert_digit(s):
    s = s.split('.')
    s = s[0]
    return int(s)


def crawl_naver_webtoon(episode_url):
    html = requests.get(episode_url).text
    soup = BeautifulSoup(html, 'html.parser')
    comic_title = ' '.join(soup.select('.comicinfo h2')[0].text.split())
    ep_title = ' '.join(soup.select('.tit_area h3')[0].text.split())

    for img_tag in soup.select('.wt_viewer img'):
        image_file_url = img_tag['src']
        image_dir_path = os.path.join(os.path.dirname(__file__), comic_title, ep_title, "img")
        image_name = os.path.basename(image_file_url)
        image_name_splited = image_name.split('_')
        image_file_path = os.path.join(image_dir_path, image_name_splited[len(image_name_splited)-1])

        if not os.path.exists(image_dir_path):
            os.makedirs(image_dir_path)

        print(image_file_path)

        headers = {'Referer': episode_url}
        image_file_data = requests.get(image_file_url, headers=headers).content
        open(image_file_path, 'wb').write(image_file_data)

    os.chdir(image_dir_path)
    img = []
    for file in os.listdir(image_dir_path):
        if file.endswith('.jpg'):
            img.append(file)
    img = sorted(img, key=convert_digit)
    print(img)
    image = []
    for i in range(len(img)):
        image.append(Image.open(img[i]))
    height = 0
    width_list = []
    for file in image:
        width_list.append(file.width)
        height += file.height
    width = max(width_list)

    with Image.new('RGB', (width, height), (255, 255, 255)) as canvas:
        canvas.paste(image[0], box=(0, 0))
        now_posit = 0
        for i in range(1, len(width_list)):
            now_posit += image[i-1].height
            canvas.paste(image[i], box=(0, now_posit))
        canvas.save(os.path.join(os.path.dirname(__file__), comic_title, ep_title, ep_title+".jpg"))

    print('Completed !')


if __name__ == '__main__':
    episode_url = 'https://comic.naver.com/webtoon/detail.nhn?titleId=670143&no=208&weekday=wed'
    crawl_naver_webtoon(episode_url)

import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

def recommended_product(category, price_int):
  url =  "http://search.danawa.com/dsearch.php?query=" + category
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
  res = requests.get(url, headers=headers)
  res.raise_for_status()
  soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦
  global suggest_list
  suggest_list = []

  # li 태그 중에서 클래스가 prod_item으로 시작하는 모든 값
  items2 = soup.find_all('li', attrs={'id':re.compile('^productItem')}) 

  for item in items2:
      name = item.find('p', attrs={'class':'prod_name'}).a.get_text().strip() # 제품명
      price = item.find('p', attrs={'class':'price_sect'}).a.strong.get_text() # 가격
      second_price = item.find('p', attrs={'class':'price_sect'}).a.strong.get_text().replace(',', '') # 가격 비교용
      link = item.find('p', attrs={'class':'prod_name'}).a['href'] # 링크
      imgs = item.select_one('.thumb_image > a > img').get("data-src") # 사진1
      if imgs == None:
          imgs = item.select_one('.thumb_image > a > img').get('data-original') # 사진2
          if imgs == None:
              imgs = item.select_one('.thumb_image > a > img').get("src") # 사진3

      suggest_lists = {
          'name' : name,
          'price' : price,
          'second_price' : int(second_price), # 가격 비교용
          'link' : link,
          'img' : imgs,
      }
      suggest_list.append(suggest_lists) 

  return suggest_list
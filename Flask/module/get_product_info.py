import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

def get_product_info(product_link):
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
  res2 = requests.get(product_link, headers=headers)
  res2.raise_for_status()
  soup2 = BeautifulSoup(res2.text, 'html.parser') #가져온 문서를 html 객체로 만듦

  product_data = []
  items = soup2.find('div', attrs={'class':'summary_info'})

  global pimg, pname, p_price, petc # 장바구니에 담을 이미지, 이름, 가격, 세부정보

  pimg = items.select_one('#baseImage').get("src") # 사진
  pname = items.select_one('div.top_summary > h3 > span').get_text()
  p_price = items.select_one('div.detail_summary > div.summary_left > div.lowest_area > div.lowest_top > div.row.lowest_price > span.lwst_prc > a > em').get_text()
  petc = items.select_one('div.top_summary > div > div.sub_dsc > div > dl > dd > div > div').get_text().replace(' ','')
  company = items.select_one('#makerTxtArea').get_text().replace('\n', '').replace('\t', '').replace('제조사:', '').replace(' ', '') # 제조사
  product_lists = {
      'img' : pimg,
      'name' : pname,
      'price' : p_price,
      'etc' : petc,
      'company' : company
  }
  product_data.append(product_lists) 

  return product_data, pimg, pname, p_price, petc
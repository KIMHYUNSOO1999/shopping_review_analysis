import requests
import re
from bs4 import BeautifulSoup

def search(search1):

  
  url =  "http://search.danawa.com/dsearch.php?query=" + search1
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
  res = requests.get(url, headers=headers)
  res.raise_for_status()
  soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

  search_list = []
  # li 태그 중에서 클래스가 prod_item으로 시작하는 모든 값
  items2 = soup.find_all('li', attrs={'id':re.compile('^productItem')}) 

  for item in items2:
      name = item.find('p', attrs={'class':'prod_name'}).a.get_text().strip() # 제품명
                      
      price = item.find('p', attrs={'class':'price_sect'}).a.strong.get_text() # 가격
          
      link = item.find('p', attrs={'class':'prod_name'}).a['href'] # 링크
          
      etc = item.select_one('.spec_list').get_text().replace("\t","").replace("\n","") # 제품 세부 설명
      
      imgs = item.select_one('.thumb_image > a > img').get("data-src") # 사진
      if imgs == None:
          imgs = item.select_one('.thumb_image > a > img').get('data-original') # 사진
          if imgs == None:
              imgs = item.select_one('.thumb_image > a > img').get("src") # 사진

      search_lists = {
          'name' : name,
          'price' : price,
          'link' : link,
          'img' : imgs,
          'etc' : etc
      }
      search_list.append(search_lists)

  return search_list
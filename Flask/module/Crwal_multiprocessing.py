import requests
import re
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import time
from multiprocessing import Process, Queue, Pool

def get_count(value):

  link = "https://prod.danawa.com/info/?pcode=11057175&keyword=%EA%B9%80%EC%B9%98&cate=1622479#bookmark_cm_opinion"
  #link = value

  m = re.search('pcode=(.+?)&keyword', link)
  global code
  if m:
      code = m.group(1)

  url = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=1"
  headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
  res = requests.get(url, headers=headers)
  res.raise_for_status()
  soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦
  count = soup.select_one('#danawa-prodBlog-companyReview-button-tab-companyReview > strong').get_text()

  global first, second, third, fourth, fifth, sixth, review_page
  review_page = round(int(count.replace(',', '')) / 10)  # 리뷰 총 페이지 수 
  devide = int(count.replace(',', '')) / 6
  first = round(devide / 10)
  second = round((devide * 2) / 10)
  third = round((devide * 3) / 10)
  fourth = round((devide * 4) / 10)
  fifth = round((devide * 5) / 10)
  sixth = round((devide * 6) / 10)

  return count

def testfirst():
  global first_review_list
  first_review_list = []
  for i in tqdm(range(1, first)):

    url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url2, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

    item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

    for res in item:
        review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
        mall = res.find('img')['src'] # 쇼핑몰 로고
        date = res.select_one('.date').get_text() # 리뷰 작성 날짜
        name = res.select_one('.name').get_text() # 작성자 아이디(이름)
        star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
        review_lists = {
            'review' : review,
            'mall_logo' : mall,
            'date' : date,
            'name' : name,
            'star_score' : star_score
        }
        first_review_list.append(review_lists)

  df = pd.DataFrame(first_review_list)
  df.to_csv('first_review.csv', encoding='utf-8-sig')

  

def testsecond():
  global second_review_list
  second_review_list = []
  for i in tqdm(range(first, second)):
      url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
      res = requests.get(url2, headers=headers)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

      item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

      for res in item:
          review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
          mall = res.find('img')['src'] # 쇼핑몰 로고
          date = res.select_one('.date').get_text() # 리뷰 작성 날짜
          name = res.select_one('.name').get_text() # 작성자 아이디(이름)
          star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
          review_lists = {
              'review' : review,
              'mall_logo' : mall,
              'date' : date,
              'name' : name,
              'star_score' : star_score
          }
          second_review_list.append(review_lists)
  df = pd.DataFrame(second_review_list)
  df.to_csv('second_review.csv', encoding='utf-8-sig')


def testthird():
  global third_review_list
  third_review_list = []
  for i in tqdm(range(second, third)):
      url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
      res = requests.get(url2, headers=headers)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

      item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

      for res in item:
          review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
          mall = res.find('img')['src'] # 쇼핑몰 로고
          date = res.select_one('.date').get_text() # 리뷰 작성 날짜
          name = res.select_one('.name').get_text() # 작성자 아이디(이름)
          star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
          review_lists = {
              'review' : review,
              'mall_logo' : mall,
              'date' : date,
              'name' : name,
              'star_score' : star_score
          }
          third_review_list.append(review_lists)
  df = pd.DataFrame(third_review_list)
  df.to_csv('third_review.csv', encoding='utf-8-sig')

        
def testfourth():
  global fourth_review_list
  fourth_review_list = []
  for i in tqdm(range(third, fourth)):
      url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
      res = requests.get(url2, headers=headers)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

      item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

      for res in item:
          review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
          mall = res.find('img')['src'] # 쇼핑몰 로고
          date = res.select_one('.date').get_text() # 리뷰 작성 날짜
          name = res.select_one('.name').get_text() # 작성자 아이디(이름)
          star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
          review_lists = {
              'review' : review,
              'mall_logo' : mall,
              'date' : date,
              'name' : name,
              'star_score' : star_score
          }
          fourth_review_list.append(review_lists)
  df = pd.DataFrame(fourth_review_list)
  df.to_csv('fourth_review.csv', encoding='utf-8-sig')



def testfifth():  
  global fifth_review_list
  fifth_review_list = []
  for i in tqdm(range(fourth, fifth)):
      url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
      res = requests.get(url2, headers=headers)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

      item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

      for res in item:
          review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
          mall = res.find('img')['src'] # 쇼핑몰 로고
          date = res.select_one('.date').get_text() # 리뷰 작성 날짜
          name = res.select_one('.name').get_text() # 작성자 아이디(이름)
          star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
          review_lists = {
              'review' : review,
              'mall_logo' : mall,
              'date' : date,
              'name' : name,
              'star_score' : star_score
          }
          fifth_review_list.append(review_lists)
  df = pd.DataFrame(fifth_review_list)
  df.to_csv('fifth_review.csv', encoding='utf-8-sig')


def testsixth():
  global sixth_review_list
  sixth_review_list = []
  for i in tqdm(range(fifth, review_page+1)):
      url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + code + "&cate1Code=861&page=" + str(i)
      headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
      res = requests.get(url2, headers=headers)
      res.raise_for_status()
      soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

      item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})

      for res in item:
          review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
          mall = res.find('img')['src'] # 쇼핑몰 로고
          date = res.select_one('.date').get_text() # 리뷰 작성 날짜
          name = res.select_one('.name').get_text() # 작성자 아이디(이름)
          star_score = int(res.select_one('.star_mask').get_text().replace("점", ""))# 별점 0, 20, 40, 60, 80, 100
          review_lists = {
              'review' : review,
              'mall_logo' : mall,
              'date' : date,
              'name' : name,
              'star_score' : star_score
          }
          sixth_review_list.append(review_lists)
  df = pd.DataFrame(sixth_review_list)
  df.to_csv('six_review.csv', encoding='utf-8-sig')



if __name__ == "__main__":
  start = time.time()

  p1 = Process(target=testfirst)
  p2 = Process(target=testsecond)
  p3 = Process(target=testthird)
  p4 = Process(target=testfourth)
  p5 = Process(target=testfifth)
  p6 = Process(target=testsixth)

  p1.start()
  p2.start()
  p3.start() 
  p4.start() 
  p5.start() 
  p6.start() 


  p1.join()
  p2.join()
  p3.join()
  p4.join()
  p5.join()
  p6.join()

  print("소요 시간 : ", time.time() - start)


import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

def Crawl(value):

    link = value
    m = re.search('pcode=(.+?)&keyword', link)   # 상품 코드 가져오기
    if m:
        prodCode = m.group(1)

    url = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + prodCode + "&cate1Code=861&page=1"
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦
    global count
    count = soup.select_one('#danawa-prodBlog-companyReview-button-tab-companyReview > strong').get_text() # 리뷰 갯수

    review_page = round(int(count.replace(',', '')) / 10)  # 리뷰 총 페이지 수 

    # 리뷰 beautifulsoup
    global review_list, pos_review_list, neg_review_list
    review_list = []    
    pos_review_list = []
    neg_review_list = []
       
    for i in tqdm(range(1,review_page+1)):
    # for i in tqdm(range(1,21)):
        url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + prodCode + "&cate1Code=861&page=" + str(i)
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
            star_score = int(res.select_one('.star_mask').get_text().replace("점", "")) # 별점 0, 20, 40, 60, 80, 100
            if int(star_score) >= 80:
                label = 1 # 긍정 80~100점 (별 4~5개)
                pos_review_lists = {
                    'review' : review,
                    'mall_logo' : mall,
                    'date' : date,
                    'name' : name,
                    'star_score' : star_score,
                    'label' : label
                }
                pos_review_list.append(pos_review_lists)
            elif int(star_score) <= 40:
                label = 0 # 부정 0~40점 (별 0~2개)
                neg_review_lists = {
                    'review' : review,
                    'mall_logo' : mall,
                    'date' : date,
                    'name' : name,
                    'star_score' : star_score,
                    'label' : label
                }
                neg_review_list.append(neg_review_lists)
            else:
                label = 2 # 나머지(별 3개)
            review_lists = {
                'review' : review,
                'mall_logo' : mall,
                'date' : date,
                'name' : name,
                'star_score' : star_score,
                'label' : label
            }
            review_list.append(review_lists)
    df=pd.DataFrame(review_list)
    df.to_csv("danawa.csv", encoding='utf-8-sig')

    return review_list, count  # 전체 리뷰, 긍정 리뷰, 부정 리뷰, 리뷰 갯수
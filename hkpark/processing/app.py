from flask import Flask, render_template, request, url_for, redirect
import requests
import re
from bs4 import BeautifulSoup
import re

from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from tqdm import tqdm
import csv

from konlpy.tag import Kkma
import pandas as pd
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt

from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

@app.route('/')
def hello_world() :
    return render_template("search.html", img_file ="image/pin_7.JPG")

# ===================================================== 에러 페이지 ==============================================================================
@app.route('/error')
def page_not_found():
    return render_template('error.html') #, 500

@app.route('/result', methods=['GET', 'POST'])
# ======================================================== 상품 찾아오기 ======================================================================
def result():

    search1 = request.form['input'] # 입력한 단어

    url =  "http://search.danawa.com/dsearch.php?query=" + search1
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦

    search_list = []
    try:
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

    except:  # 검색 결과가 없을때
    
        return redirect(url_for('page_not_found'))
        
    return render_template("result.html", 
                            search = search1,
                            search_list = search_list)

@app.route("/<pagename>/<name>")
def page(pagename, name):

    product_name = name
    
    #==================================================== 링크를 다시 가져오기 위한 크롤링 ======================================================================
    url = "https://search.danawa.com/dsearch.php?k1=" + product_name
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 lxml 객체로 만듦

    # li 태그 중에서 클래스가 productItem으로 시작하는 모든 값
    items2 = soup.find_all('li', attrs={'id':re.compile('^productItem')}) 

    # 링크 가져오기
    for item in items2[:1]:
        link = item.find('p', attrs={'class':'prod_name'}).a['href'] # 링크 첫번째 항목까지만

        product_lists = {
            'link' : link
        }

        value = product_lists['link'] # 리스트에서 link에 해당하는 값


    # #==================================================== 리뷰 크롤링 ======================================================================
    product_link = value + "#bookmark_cm_opinion" # 리뷰를 크롤링하기 위해 추가한거...

    # lst = link.split("pcode=")
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
    global review_list
    review_list = []    
       
    # for i in tqdm(range(1,review_page+1)):
    for i in tqdm(range(1,20)):
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
            review_lists = {
                'review' : review,
                'mall_logo' : mall,
                'date' : date,
                'name' : name,
                'star_score' : star_score,
            }
            review_list.append(review_lists)
    df=pd.DataFrame(review_list)
    df.to_csv("C:/Users/parkh/OneDrive/바탕 화면/한라/danawa.csv", encoding='utf-8-sig')
    
    review_len = len(review_lists) # 행 개수

    # ============================================== 클릭한 제품 이름, 사진, 가격, 세부내용 ======================================================================
    res2 = requests.get(product_link, headers=headers)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html.parser') #가져온 문서를 html 객체로 만듦

    product_data = []
    items = soup2.find('div', attrs={'class':'summary_info'})
    
    pimg = items.select_one('#baseImage').get("src") # 사진
    pname = items.select_one('div.top_summary > h3 > span').get_text()
    p_price = items.select_one('div.detail_summary > div.summary_left > div.lowest_area > div.lowest_top > div.row.lowest_price > span.lwst_prc > a > em').get_text()
    petc = items.select_one('div.top_summary > div > div.sub_dsc > div > dl > dd > div > div').get_text().replace(' ','')
    product_lists = {
        'img' : pimg,
        'name' : pname,
        'price' : p_price,
        'etc' : petc
    }
    product_data.append(product_lists)    

    # ============================================================== 워드클라우드 ======================================================================
    kkma = Kkma()

    df=pd.read_csv("C:/Users/parkh/OneDrive/바탕 화면/한라/danawa.csv")
    del df["Unnamed: 0"]

    article_list=[]

    for i in range(10):
        article_list.append(df.loc[i,'review'])

    kkma.pos(article_list[0])

    pos_list = ["NNG", "NNP"]
    tag_sentence_list = []

    now = 0
    for article in article_list:
        now += 1
        print(now, end="\r")
        sentence_list = kkma.sentences(article)
        tag_sentence = []
        for sentence in sentence_list:
            tag_list = kkma.pos(sentence)
            for word, pos in tag_list:
                if pos in pos_list and word and len(word) > 1:
                    tag_sentence.append(word)
        tag_sentence_list.append(tag_sentence)

    word_frequency = {}

    for tag_sentence in tag_sentence_list:
        for word in tag_sentence:
            if word in word_frequency.keys():
                word_frequency[word] += 1
            else:
                word_frequency[word] = 1

    word_count = []
    for word, freq in word_frequency.items():
        word_count.append([word, freq])
    word_count.sort(key=lambda elem: elem[1], reverse=True)

    for word, freq in word_count[:20]:
        print(word + "\t" + str(freq))
        
    noun_string = ""

    for tag_sentence in tag_sentence_list:

        import random
        random.shuffle(tag_sentence)
        for word in tag_sentence:
            noun_string += word + " "

    noun_string = noun_string.strip()

    font_path='C:/Windows/Fonts/NanumGothic.ttf'  
    background_color="white"      
    margin=10                     
    min_font_size=10              
    max_font_size=150             
    width=500                     
    height=500                   
    wc = WordCloud(font_path=font_path, background_color=background_color, \
                margin=margin, min_font_size=min_font_size, \
                max_font_size=max_font_size, width=width, height=height, prefer_horizontal = True)

    wc.generate(noun_string)


    plt.figure(figsize=(15, 15))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('C:/Users/parkh/OneDrive/바탕 화면/한라/static/image/wordcloud.png')
    #plt.show()  


    return render_template(f'{pagename}.html', 
                                name = name, 
                                value=product_link, 
                                review_list = review_list,
                                product_data = product_data,
                                shoplink = value,
                                wordcloud_img ="image/wordcloud.png")

# =========================================== 리뷰 보기 버튼 클릭 시 분석한 리뷰를 보여주기 위한 페이지 ===================================================   
def get_users(offset=0, per_page=10):
    return review_list[offset: offset + per_page]

@app.route('/review', methods=['GET', 'POST'])
def review():
    review = review_list
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(review_list)
    pagination_users = get_users(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    
    
    return render_template('review.html', 
                            review = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = count)

    


if __name__ == '__main__':
    app.run()


from flask import Flask, render_template, request, url_for, redirect, session, flash
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
import os
import pymysql

app = Flask(__name__)
app.secret_key = os.urandom(24)


# ================================================================ 메인(검색) 페이지 ========================================================================
@app.route('/')
def hello_world():
    return render_template("search.html")
# ================================================================= 특정 장바구니 상품만 삭제 =============================================
@app.route('/delete',  methods=['GET','POST'])
def delete():
    user_id = session['user_id']
    pname = request.form.get('pname')

    db = pymysql.connect(
        user    = 'root',
        passwd  = 'rainbow@6861',
        port    = 3306,
        host    = 'localhost',
        db      = 'sqldb',
        charset = 'utf8'
    )
    cursor = db.cursor()
    cursor.execute('DELETE FROM shop_list WHERE uid = %s AND product_name = %s', [user_id, pname])   # 아이디와 해당 제품 이름에 해당하는거만 삭제
    db.commit()
    db.close()

    flash("삭제되었습니다.")

    return redirect(url_for('shopping_cart'))

# ==================================================================== 장바구니 비우기 =======================================================================
@app.route('/cart_delete')
def cart_delete():
        # 'DELETE FROM shop_list WHERE uid=%'
    id = session['user_id']

    db = pymysql.connect(
        user    = 'root',
        passwd  = 'rainbow@6861',
        port    = 3306,
        host    = 'localhost',
        db      = 'sqldb',
        charset = 'utf8'
    )

    cursor = db.cursor()
    cursor.execute('DELETE FROM shop_list WHERE uid=%s', [id])   # 해당 아이디에 해당하는 제품들 모두 삭제
    db.commit()
    db.close()

    flash("장바구니 내역을 삭제하였습니다.")
    
    return redirect(url_for('shopping_cart')) # 장바구니를 비우면 /shopping_cart로 라우팅

# ==================================================================== 장바구니 =============================================================================
@app.route('/shopping_cart')
def shopping_cart():

    id = session['user_id'] # 로그인한 유저 아이디(세션 아이디)

    db = pymysql.connect(
        user    = 'root',
        passwd  = 'rainbow@6861',
        port    = 3306,
        host    = 'localhost',
        db      = 'sqldb',
        charset = 'utf8'
    )
    cursor = db.cursor()
    # 장바구니에 해당 유저가 담은 제품 있는지
    cursor.execute('SELECT product_name, product_price, product_img, product_etc, product_link FROM user, shop_list WHERE user.user_id = shop_list.uid AND user_id=%s', [id])
    account = cursor.fetchall()
    shop_list = []
    if account: # 장바구니에 상품이 존재하면 데이터를 리스트에 저장 후 cart 페이지로
        for row in account:
            list = {
                'product_name' : row[0],
                'product_price' : row[1],
                'product_img' : row[2],
                'product_etc' : row[3],
                'product_link' : row[4],
            }
            shop_list.append(list)
        db.close()

        return render_template("cart.html", shop_list = shop_list)
    else: # 장바구니가 비어있으면 empty_cart 페이지로

        db.close()
        return render_template("empty_cart.html")        # db에서 값 뽑아내는거만 하면 됨


# =================================================================== 장바구니에 담기 ============================================================
@app.route('/cart')
def cart():
    link = value
    img = pimg
    name = pname
    price = p_price
    etc = petc
    id = session['user_id']
    # if id == None:


    db = pymysql.connect(
        user    = 'root',
        passwd  = 'rainbow@6861',
        port    = 3306,
        host    = 'localhost',
        db      = 'sqldb',
        charset = 'utf8'
    )
    cursor = db.cursor()
    # 장바구니에 중복된 제품이 있는지 확인
    cursor.execute('SELECT shop_list.product_name FROM user, shop_list WHERE shop_list.uid=%s and product_name=%s', [id, name])
    account = cursor.fetchone()

    if account: # 중복된 제품이 있으면
        flash('이미 장바구니에 담은 상품입니다.')
        return redirect(url_for('main'))
        
    else:       # 중복된 제품이 없다면 장바구니에 추가
        cursor.execute('INSERT INTO shop_list (uid, product_name, product_price, product_img, product_etc, product_link) VALUES (%s, %s, %s, %s, %s ,%s)', [id, name, price, img, etc, link])
        db.commit()
        db.close()

        flash('장바구니에 추가되었습니다.')
        return redirect(url_for('main'))

    return redirect(url_for('modal.html'))






# ==================================================================== 로그 아웃 ========================================================================================
@app.route('/logout')
def logout():
    session.clear()
    return render_template("search.html")  # 로그아웃 버튼 클릭 시 세션 초기화(로그아웃) 후 첫 페이지로 이동

# =================================================================== 로그인 페이지 =====================================================================================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user_password = request.form['user_password']

        db = pymysql.connect(
            user    = 'root',
            passwd  = 'rainbow@6861',
            port    = 3306,
            host    = 'localhost',
            db      = 'sqldb',
            charset = 'utf8'
        )

        cursor = db.cursor()
        cursor.execute('SELECT * FROM user WHERE user_id = %s and user_passwd = %s', [user_id, user_password]) # 아이디, 패스워드 존재 확인
        account = cursor.fetchone()

        if account: # 유저가 있으면, 로그인 성공(세션 만들기)
            session['loggedin'] = True
            session['user_id'] = request.form['user_id']

            return render_template("search.html")
        
        else: # 아이디와 비밀번호가 존재하지 않거나 다르면
            flash('아이디, 비밀번호를 확인해주세요', category="error")
            return render_template("login.html")

    return render_template("login.html")

# ================================================================ 회원가입 페이지 =============================================================================
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['id']
        user_password = request.form['password']
        user_email = request.form['email']
        user_nickname = request.form['nickname']
        msg = ''

        db = pymysql.connect(
            user    = 'root',
            passwd  = 'rainbow@6861',
            port    = 3306,
            host    = 'localhost',
            db      = 'sqldb',
            charset = 'utf8'
        )
        cursor = db.cursor()

        cursor.execute('SELECT * FROM user WHERE user_id=%s', [user_id])
        account = cursor.fetchone()

        if account: # 아이디 중복
            flash('이미 사용중인 아이디 입니다.', category="error")
            return render_template('signup.html')

        else: # 아니면 회원가입 완료.  회원가입 완료 알람 수정 필요
            sql = 'INSERT INTO user (user_id, user_passwd, user_email, user_nickname) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (user_id, user_password, user_email, user_nickname))
            
            db.commit()
            db.close()

            flash('회원가입 성공!', category="error")
            return render_template('login.html')


    else:
        return render_template('signup.html')
 
    return render_template("signup.html")

# ======================================================================== 에러 페이지 =============================================================================================
@app.route('/error')
def page_not_found():
    return render_template('error.html') #, 500

@app.route('/result', methods=['GET', 'POST'])
# =========================================================================== 상품 찾아오기 =======================================================================================
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
    
    #================================================================== 링크를 다시 가져오기 위한 크롤링 ======================================================================
    url = "https://search.danawa.com/dsearch.php?k1=" + product_name

    global value
    

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


    # ==================================================================== 리뷰 크롤링 ================================================================================
    product_link = value + "#bookmark_cm_opinion" # 리뷰를 크롤링하기 위해 추가한거...

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

    # ====================================================================== 클릭한 제품 이름, 사진, 가격, 세부내용 ================================================================================
    res2 = requests.get(product_link, headers=headers)
    res2.raise_for_status()
    soup2 = BeautifulSoup(res2.text, 'html.parser') #가져온 문서를 html 객체로 만듦

    global product_data
    product_data = []
    items = soup2.find('div', attrs={'class':'summary_info'})

    global pimg, pname, p_price, petc # 장바구니에 담을 이미지, 이름, 가격, 세부정보

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

    # ================================================================================ 워드클라우드 ======================================================================================
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

    return redirect(url_for('main')) # 작업이 끝나면 main 으로 라우팅


# ============================================================== 리뷰, 워드클라우드 등 결과 표시 페이지 ================================================================================
@app.route('/main', methods=['GET', 'POST'])
def main():
    # reviews = review_list
    plink = value
    product_info = product_data
    return render_template('modal.html', shoplink = plink, product_data = product_info)

# ============================================================== 리뷰 보기 버튼 클릭 시 분석한 리뷰를 보여주기 위한 페이지 ==============================================================   
def get_users(offset=0, per_page=10):
    return review_list[offset: offset + per_page]

@app.route('/review', methods=['GET', 'POST'])
def review():

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
                            review_count = count,
                            )

    


if __name__ == '__main__':
    app.run(debug=True)


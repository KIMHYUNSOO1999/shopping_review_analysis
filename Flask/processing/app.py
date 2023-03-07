from flask import Flask, render_template, request, url_for, redirect, session, flash
import requests
import re
from bs4 import BeautifulSoup
import re

import pandas as pd
from tqdm import tqdm
import csv

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns

from flask_paginate import Pagination, get_page_args
import os
import pymysql
import pymysql.cursors
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import bcrypt

from konlpy.tag import Okt
from collections import Counter

import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow_addons.optimizers import RectifiedAdam

tf.keras.optimizers.RectifiedAdam = RectifiedAdam

app = Flask(__name__)
app.secret_key = os.urandom(24)
# ================================================================ 시작 전 모델 로드 =================================================================
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = "klue/bert-base"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
global model
model  = tf.keras.models.load_model(BASE_DIR/'model/best_model.h5',
                                                    custom_objects={'TFBertForSequenceClassification': TFBertForSequenceClassification})


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
        user_password = request.form['user_password'].encode('utf-8') # 입력된 비밀번호를 바이트 코드로

        db = pymysql.connect(
            user    = 'root',
            passwd  = 'rainbow@6861',
            port    = 3306,
            host    = 'localhost',
            db      = 'sqldb',
            charset = 'utf8'
        )

        cursor = db.cursor(pymysql.cursors.DictCursor)
        # cursor.execute('SELECT * FROM user WHERE user_id = %s and user_passwd = %s', [user_id, user_password]) # 아이디, 패스워드 존재 확인
        cursor.execute('SELECT * FROM user WHERE user_id = %s', [user_id])
        account = cursor.fetchone()
        if account:
            origin_password = bytes.fromhex(account['user_password']) # 기존 저장된 값을 비교하기 위해 hex에서 byte로 
        
            check = bcrypt.checkpw(user_password, origin_password) # 입력한 비밀번호와 저장된 비밀번호 체크

            if account and check: # 유저와 암호화된 패스워드 확인 시 로그인 성공(세션 만들기)
                session['loggedin'] = True
                session['user_id'] = request.form['user_id']

                return render_template("search.html")
            
            else: # 아이디와 비밀번호가 존재하지 않거나 다르면
                flash('아이디, 비밀번호를 확인해주세요', category="error")
                return render_template("login.html")
        else:
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

        # 입력한 비밀번호를 해싱을 위해 바이트 코드로 변환 후 해싱, 저장을 위해 16진수로 변환
        hash_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).hex()

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
            sql = 'INSERT INTO user (user_id, user_password, user_email, user_nickname) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (user_id, hash_password, user_email, user_nickname))

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
    global review_list, pos_review_list, neg_review_list
    review_list = []    
    pos_review_list = []
    neg_review_list = []
       
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
    company = items.select_one('#makerTxtArea').get_text().replace('\n', '').replace('\t', '').replace('제조사:', '').replace(' ', '') # 제조사
    product_lists = {
        'img' : pimg,
        'name' : pname,
        'price' : p_price,
        'etc' : petc,
        'company' : company
    }
    product_data.append(product_lists) 

    df_prod = pd.DataFrame(product_data)   
    etc_prod = df_prod['etc'][0]
    cate = etc_prod.split("/", 1)
    #cate[0]
    category = cate[0]

    company = df_prod['company'][0]

    # =============================================================================== 제조사, 카테고리 관련 제품 추천 =======================================================================

    sug(company, category)

    # ================================================================================ 텍스트 긍부정 라벨  ======================================================================================

    get_title_score2()

   # ================================================================================ 워드클라우드 ===========================================================================================
    okt = Okt()

    df2 = pd.read_csv('danawa_label.csv', encoding='CP949')
    del df2['Unnamed: 0']
    good_text=[]
    bad_text=[]

    for i in range(len(df2)):
        if df2.loc[i,'label']==1:
            good_text.append(df2.loc[i,'review'])
        else:
            bad_text.append(df2.loc[i,'review'])

    good_text = [x for x in good_text if pd.isnull(x) == False]
    bad_text = [x for x in bad_text if pd.isnull(x) == False]

    okt = Okt()

    good_morphs = []
    bad_morphs = []

    for i in range(len(good_text)):
        try:
            good_morphs.append(okt.pos(good_text[i]))
        except UnicodeDecodeError:
            pass

    for i in range(len(bad_text)):
        try:
            bad_morphs.append(okt.pos(bad_text[i]))
        except UnicodeDecodeError:
            pass

    good_list=[] 
    bad_list=[] 

    for sentence in good_morphs : 
        for word, tag in sentence : 
            if tag in ['Noun','Adjective']:
                good_list.append(word)

    for sentence in bad_morphs : 
        for word, tag in sentence : 
            if tag in ['Noun','Adjective']:
                bad_list.append(word)
     
    good_count = Counter(good_list)
    good_word = dict(good_count.most_common())

    bad_count = Counter(bad_list)
    bad_word = dict(bad_count.most_common())

    import matplotlib 
    from IPython.display import set_matplotlib_formats 
    matplotlib.rc('font',family = 'Malgun Gothic') 
    set_matplotlib_formats('retina') 
    matplotlib.rc('axes',unicode_minus = False)

    max = 100
    good_top = {}
    bad_top = {}

    for word, counts in good_count.most_common(max):
        good_top[word] = counts 

    for word, counts in bad_count.most_common(max):
        bad_top[word] = counts  

    # 긍정 워드 클라우드
    alice_coloring = np.array(Image.open('static/image/cloud_image.png'))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(font_path = 'font/BinggraeⅡ-Bold.ttf', background_color='white',colormap = "YlOrRd",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(good_top)

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('static/image/pos_wordcloud.png', bbox_inches='tight')

    # 부정 워드 클라우드
    alice_coloring = np.array(Image.open('static/image/cloud_image.png'))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(font_path = 'font/BinggraeⅡ-Bold.ttf', background_color='white',colormap = "plasma",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(bad_top) 

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('static/image/neg_wordcloud.png', bbox_inches='tight')

    # 도넛 차트
    donut(neg_per, pos_per)

    # 바 차트
    bar(five_count, four_count, three_count, two_count, one_count, zero_count)

    return redirect(url_for('main'))

    
# ============================================================== 리뷰, 워드클라우드 등 결과 표시 페이지 ================================================================================
@app.route('/main', methods=['GET', 'POST'])
def main():

    plink = value
    product_info = product_data

    # 긍정 리뷰 top 3개
    pos_review = []
    for i in good_text[:3]:
        positive_review ={
            'review' : i["review"],
            'name' : i["name"],
            'mall_logo' : i["mall_logo"],
            'date' : i["date"],
        }
        pos_review.append(positive_review)

    # 부정 리뷰 top 3개
    neg_review = []
    for i in bad_text[:3]:
        negative_review ={
            'review' : i["review"],
            'name' : i["name"],
            'mall_logo' : i["mall_logo"],
            'date' : i["date"],
        }
        neg_review.append(negative_review)

    return render_template('modal.html',                          
                            shoplink = plink, 
                            product_data = product_info,
                            pos_review = pos_review,
                            neg_review = neg_review,
                            good_text=good_text,
                            bad_text=bad_text,
                            suggest_list = suggest_list)

# ============================================================== 리뷰 보기 버튼 클릭 시 분석한 리뷰를 보여주기 위한 페이지 (전체 리뷰)==============================================================   
def get_users(offset=0, per_page=10): # 전체
    return label_review[offset: offset + per_page]

@app.route('/review', methods=['GET', 'POST'])
def review():

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(label_review)
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

# =================================================================================== 별 1개  리뷰 =====================================================================================
def get_users_one(offset=0, per_page=10): # 별 1개
    return one_star[offset: offset + per_page]

@app.route('/one', methods=['GET', 'POST'])
def one():
    global one_star
    one_star = []
    for i in review_list:
        if i["star_score"] == 20:
            one = {
                'review' : i["review"],
                'name' : i["name"],
                'mall_logo' : i["mall_logo"],
                'date' : i["date"],
                'star' : i["star_score"]
            }
            one_star.append(one)

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    total = len(one_star)
    pagination_users = get_users_one(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    one_count = len(one_star)
    return render_template('one_star.html', 
                            one_star = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = one_count)

# =================================================================================== 별 2개  리뷰 =====================================================================================
def get_users_two(offset=0, per_page=10): # 별 2개
    return two_star[offset: offset + per_page]

@app.route('/two', methods=['GET', 'POST'])
def two():
    global two_star
    two_star = []
    for i in review_list:
        if i["star_score"] == 40:
            two = {
                'review' : i["review"],
                'name' : i["name"],
                'mall_logo' : i["mall_logo"],
                'date' : i["date"],
                'star' : i["star_score"]
            }
            two_star.append(two)

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    total = len(two_star)
    pagination_users = get_users_two(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    two_count = len(two_star)
    return render_template('two_star.html', 
                            two_star = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = two_count)

# =================================================================================== 별 3개  리뷰 =====================================================================================
def get_users_three(offset=0, per_page=10): # 별 3개
    return three_star[offset: offset + per_page]

@app.route('/three', methods=['GET', 'POST'])
def three():
    global three_star
    three_star = []
    for i in review_list:
        if i["star_score"] == 60:
            three = {
                'review' : i["review"],
                'name' : i["name"],
                'mall_logo' : i["mall_logo"],
                'date' : i["date"],
                'star' : i["star_score"]
            }
            three_star.append(three)

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    total = len(three_star)
    pagination_users = get_users_three(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    three_count = len(three_star)
    return render_template('three_star.html', 
                            three_star = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = three_count)

# =================================================================================== 별 4개  리뷰 =====================================================================================
def get_users_four(offset=0, per_page=10): # 별 4개
    return four_star[offset: offset + per_page]


@app.route('/four', methods=['GET', 'POST'])
def four():
    global four_star
    four_star = []
    for i in review_list:
        if i["star_score"] == 80:
            four = {
                'review' : i["review"],
                'name' : i["name"],
                'mall_logo' : i["mall_logo"],
                'date' : i["date"],
                'star' : i["star_score"]
            }
            four_star.append(four)

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    total = len(four_star)
    pagination_users = get_users_four(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    four_count = len(four_star)
    return render_template('four_star.html', 
                            four_star = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = four_count)

# =================================================================================== 별 5개  리뷰 =====================================================================================
def get_users_five(offset=0, per_page=10): # 별 5개
    return five_star[offset: offset + per_page]

@app.route('/five', methods=['GET', 'POST'])
def five():
    global five_star
    five_star = []
    for i in review_list:
        if i["star_score"] == 100:
            five = {
                'review' : i["review"],
                'name' : i["name"],
                'mall_logo' : i["mall_logo"],
                'date' : i["date"],
                'star' : i["star_score"]
            }
            five_star.append(five)

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    total = len(five_star)
    pagination_users = get_users_five(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    five_count = len(five_star)
    return render_template('five_star.html', 
                            five_star = pagination_users,
                            page=page,
                            per_page=per_page,
                            pagination=pagination,
                            review_count = five_count)
# ======================================================================================= 모델 ========================================================================================================

def convert_data(X_data,MAX_SEQ_LEN,tokenizer):
    # BERT 입력으로 들어가는 token, mask, segment, target 저장용 리스트
    tokens, masks, segments, targets = [], [], [], []
    
    for X in (X_data):
        # token: 입력 문장 토큰화
        token = tokenizer.encode(X, truncation = True, padding = 'max_length', max_length = MAX_SEQ_LEN)
        
        # Mask: 토큰화한 문장 내 패딩이 아닌 경우 1, 패딩인 경우 0으로 초기화
        num_zeros = token.count(0)
        mask = [1] * (MAX_SEQ_LEN - num_zeros) + [0] * num_zeros
        
        # segment: 문장 전후관계 구분: 오직 한 문장이므로 모두 0으로 초기화
        segment = [0]*MAX_SEQ_LEN

        tokens.append(token)
        masks.append(mask)
        segments.append(segment)

    # numpy array로 저장
    tokens = np.array(tokens)
    masks = np.array(masks)
    segments = np.array(segments)
  
    return [tokens, masks, segments]


# 최고 성능의 모델 불러오기
def get_title_score2():
    import warnings
    warnings.filterwarnings('ignore')

    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    df = pd.read_csv(BASE_DIR/'danawa.csv')
    # df = df.drop('Unnamed: 0',axis= 1)

    df['review'] = df['review'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
    df['review'].nunique()
    df.drop_duplicates(subset=['review'], inplace=True)

    X_data = df['review']
    MAX_SEQ_LEN = 80
    tokenizer = BertTokenizer.from_pretrained('klue/bert-base')

    # train 데이터를 Bert의 Input 타입에 맞게 변환

    train_x= convert_data(X_data,MAX_SEQ_LEN,tokenizer)

    # print(train_x)
    predicted_value = model.predict(train_x)
    predicted_label = np.argmax(predicted_value, axis = 1)

    global label_review

    data = {
        'review':df['review'],
        'mall_logo':df['mall_logo'],
        'date':df['date'],
        'name':df['name'],
        'star_score':df['star_score'],
        'label':predicted_label
    }

    df_final = pd.DataFrame(data)
    df_final.to_csv(BASE_DIR/'danawa_label.csv',encoding='CP949')

    label_review = df_final.to_dict('records') # df를 딕셔너리 변환해서 사용

    # 긍부정 단어 퍼센트
    global pos_per, neg_per
    total = df_final['label'].count()
    pos_count = df_final[df_final['label']==1].label.count() 
    neg_count = df_final[df_final['label']==0].label.count() 

    pos_per = round((pos_count / total)*100, 2)
    neg_per = round((neg_count / total)*100, 2)

    # 별점 별 개수
    global five_count, four_count, three_count, two_count, one_count, zero_count
    five_count = df_final[df_final['star_score']==100].star_score.count() 
    four_count = df_final[df_final['star_score']==80].star_score.count() 
    three_count = df_final[df_final['star_score']==60].star_score.count() 
    two_count = df_final[df_final['star_score']==40].star_score.count() 
    one_count = df_final[df_final['star_score']==20].star_score.count() 
    zero_count = df_final[df_final['star_score']==0].star_score.count() 

    # 긍정, 부정 리뷰 리스트로 분리
    global good_text, bad_text
    good_text=[]
    bad_text=[]
    for i in range(len(df_final)):
        if df_final.loc[i,'label']==1:
            good = {
                'review':df_final.loc[i,'review'],
                'mall_logo':df_final.loc[i,'mall_logo'],
                'date':df_final.loc[i,'date'],
                'name':df_final.loc[i,'name'],
                'star_score':df_final.loc[i,'star_score'],
                'label':df_final.loc[i,'label']
            }
            good_text.append(good)
        else:
            bad = {
                'review':df_final.loc[i,'review'],
                'mall_logo':df_final.loc[i,'mall_logo'],
                'date':df_final.loc[i,'date'],
                'name':df_final.loc[i,'name'],
                'star_score':df_final.loc[i,'star_score'],
                'label':df_final.loc[i,'label']
            }
            bad_text.append(bad)

# ======================================================================================= 도넛차트 ========================================================================================================
def donut(pos, neg):
    labels = ['부정 리뷰', '긍정 리뷰']
    colors = ['#ff9999','#8fd9b6']
    frequency = [neg, pos]
    wedgeprops={'width': 0.5}
    explode = [0.05, 0.00]

    fig = plt.figure(figsize=(8,8)) 
    fig.set_facecolor('white') 
    ax = fig.add_subplot() 

    pie = ax.pie(frequency, 
                    startangle=180, 
                    counterclock=False,
                    wedgeprops=wedgeprops,
                    colors=colors,
                    labels=labels,
                    explode=explode,
                    shadow = True,
                )

    total = np.sum(frequency) ## 빈도수 총합

    sum_pct = 0 ## 백분율 초기값
    for i,l in enumerate(labels):
        ang1, ang2 = pie[0][i].theta1, pie[0][i].theta2 ## 각1, 각2
        r = pie[0][i].r ## 원의 반지름

        x = ((r+0.5)/2)*np.cos(np.pi/180*((ang1+ang2)/2)) ## 정중앙 x좌표
        y = ((r+0.5)/2)*np.sin(np.pi/180*((ang1+ang2)/2)) ## 정중앙 y좌표

        if i < len(labels) - 1:
            sum_pct += float(f'{frequency[i]/total*100:.2f}') ## 백분율을 누적한다.
            ax.text(x,y,f'{frequency[i]/total*100:.2f}%',ha='center',va='center') ## 백분율 텍스트 표시
        else: ## 총합을 100으로 맞추기위해 마지막 백분율은 100에서 백분율 누적값을 빼준다.
            ax.text(x,y,f'{100-sum_pct:.2f}%',ha='center',va='center') 

    
    plt.legend(pie[0],labels) ## 범례 표시
    plt.rcParams['font.size'] = 15
    plt.savefig('static/image/donut_chart.png', bbox_inches='tight')

# ======================================================================================= 바 차트 ========================================================================================================
def bar(five, four, three, two, one, zero):
    x = [5, 4, 3, 2, 1, 0]
    y = [five, four, three, two, one, zero]

    colors = sns.color_palette('hls',len(y)) # 색상
    plt.figure(figsize=(10,8))
    plt.bar(x, y, width=0.7, color=colors, edgecolor='black')
    plt.xlabel('별점', fontweight = "bold", fontsize=18)
    plt.ylabel('리뷰 개수', fontweight = "bold", fontsize=18)

    for i, v in enumerate(x):
        plt.text(v, y[i], str(y[i]),
                fontsize=18,
                color="black",
                fontweight = "bold",
                horizontalalignment='center',
                verticalalignment='bottom')

    plt.savefig('static/image/bar_chart.png', bbox_inches='tight')

# ====================================================================== 제조사 + 카테고리 검색 ==========================================================================
def sug(company, category):
    url =  "http://search.danawa.com/dsearch.php?query=" + company + category
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') #가져온 문서를 html 객체로 만듦
    global suggest_list
    suggest_list = []

    # li 태그 중에서 클래스가 prod_item으로 시작하는 모든 값
    items2 = soup.find_all('li', attrs={'id':re.compile('^productItem')}) 

    for item in items2[:5]:
        name = item.find('p', attrs={'class':'prod_name'}).a.get_text().strip() # 제품명
        price = item.find('p', attrs={'class':'price_sect'}).a.strong.get_text() # 가격
        link = item.find('p', attrs={'class':'prod_name'}).a['href'] # 링크
        imgs = item.select_one('.thumb_image > a > img').get("data-src") # 사진1
        if imgs == None:
            imgs = item.select_one('.thumb_image > a > img').get('data-original') # 사진2
            if imgs == None:
                imgs = item.select_one('.thumb_image > a > img').get("src") # 사진3

        suggest_lists = {
            'name' : name,
            'price' : price,
            'link' : link,
            'img' : imgs,
        }
        suggest_list.append(suggest_lists) 

plt.show()
if __name__ == '__main__':
    app.run()


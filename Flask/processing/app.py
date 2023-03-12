from flask import Flask, render_template, request, url_for, redirect, session, flash

import pandas as pd
import matplotlib.pyplot as plt
import time

from flask_paginate import Pagination, get_page_args
import os
import pymysql
import pymysql.cursors
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
import bcrypt

import tensorflow as tf
from tensorflow_addons.optimizers import RectifiedAdam

# 파이썬 파일 Import
from module import search # 제품 검색
from module import get_link # 제품 링크 얻기
from module import review_Crawl # 리뷰 크롤링
from module import get_product_info # 선택한 제품 정보 가져오기
from module import run_model # 모델 수행
from module import load_model # 모델 로드
from module import donut # 도넛 차트
from module import bar # 바 차트
from module import Recommended_Product # 제품 추천
from module import mecab_wordcloud # MeCab워드클라우드
from module import rank2 # textrank

tf.keras.optimizers.RectifiedAdam = RectifiedAdam

app = Flask(__name__)
app.secret_key = os.urandom(24)
# 모델 로드
from pathlib import Path

model = load_model.load_model()


# 메인 페이지(검색 페이지)
@app.route('/')
def hello_world():
    return render_template("search.html")

# 특정 장바구니 제품 삭제
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

# 장바구니 비우기
@app.route('/cart_delete')
def cart_delete():
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

# 장바구니
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


# 장바구니 담기
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

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return render_template("search.html")  # 로그아웃 버튼 클릭 시 세션 초기화(로그아웃) 후 첫 페이지로 이동

# 로그인 페이지
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
        cursor.execute('SELECT * FROM user WHERE user_id = %s', [user_id])
        account = cursor.fetchone()
        if account:
            origin_password = bytes.fromhex(account['user_passwd']) # 기존 저장된 값을 비교하기 위해 hex에서 byte로 
        
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

# 회원가입
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
            sql = 'INSERT INTO user (user_id, user_passwd, user_email, user_nickname) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (user_id, hash_password, user_email, user_nickname))

            db.commit()
            db.close()

            flash('회원가입 성공!', category="error")
            return render_template('login.html')


    else:
        return render_template('signup.html')
 
    return render_template("signup.html")

# 검색 결과 없을때 표시할 페이지(에러 페이지)
@app.route('/error')
def page_not_found():
    return render_template('error.html') #, 500

@app.route('/result', methods=['GET', 'POST'])
# 검색한 제품 찾아오기
def result(): # search.py
    search1 = request.form['input'] # 입력한 단어
    try:
        search_list = search.search(search1)

    except:  # 검색 결과가 없을때
    
        return redirect(url_for('page_not_found'))
        
    return render_template("result.html", 
                            search = search1,
                            search_list = search_list)

# 메인 코드
@app.route("/<pagename>/<name>")
def page(pagename, name):

    product_name = name
   
    #링크 가져오기 1
    global value
    value = get_link.get_link(product_name)
    
    # 리뷰 크롤링 2
    global review_list, count
    review_list, count = review_Crawl.Crawl(value)

    product_link = value + "#bookmark_cm_opinion" # 리뷰를 크롤링 링크, 제품 정보 링크

    # 클릭한 제품 이름, 사진, 가격, 세부 내용 3
    
    global product_data, pimg, pname, p_price, petc
    product_data, pimg, pname, p_price, petc = get_product_info.get_product_info(product_link)

    # 제조사, 카테고리 관련 제품 추천 4 
    df_prod = pd.DataFrame(product_data)   

    etc_prod = df_prod['etc'][0]
    cate = etc_prod.split("/", 1)
   
    category = cate[0]
    company = df_prod['company'][0]

    # 선택한 제품 가격을 정수로
    price_int = int(df_prod['price'][0].replace(',', ''))

    # 추천 상품
    
    suggest_list = Recommended_Product.recommended_product(category, price_int)
    sug_df = pd.DataFrame(suggest_list)

    # 선택한 제품보다 +- 50000원 
    price_sort =  sug_df[ ( (sug_df['second_price'] >= price_int - 50000) & (sug_df['second_price'] <= price_int + 50000) ) ]
    # price_sort_df = price_sort.sort_values(by='second_price')
    price_sort_df = price_sort.sort_index()

    # +- 50000원 인 제품 데이터프레임 딕셔너리로 변환
    global recommended_product_list
    range_price_item = price_sort_df.to_dict('records')
    recommended_product_list = range_price_item[:5] # 5개


    # 텍스트 긍부정 라벨 
    global good_text, bad_text, label_review
    good_text, bad_text, pos_per, neg_per, label_review, five_count, four_count, three_count, two_count, one_count, zero_count, df_one = run_model.get_title_score2()
    
    #워드클라우드
    # get_wordcloud.wordcloud()

    mecab_wordcloud.Processing_Mecab()


    # df=pd.read_csv('danawa_label.csv', encoding='cp949') 
    # df=df.dropna(axis=0)
    global Top3_good, Top3_bad
    Top3_good, Top3_bad = rank2.Processing_TextRank(df_one)

    # 도넛 차트
    global donut_per
    donut_per = donut.donut(pos_per, neg_per)

    # 바 차트
    global bar_cnt
    bar_cnt = bar.bar(five_count, four_count, three_count, two_count, one_count, zero_count)

    return redirect(url_for('main'))

    
#  리뷰, 워드클라우드 등 결과 표시 페이지 
@app.route('/main', methods=['GET', 'POST'])
def main():

    plink = value
    product_info = product_data

    # pos_review, neg_review = text_rank.text_rank(good_text, bad_text)

    bar_count = []
    bar_count.append(bar_cnt)

    # 긍정 Top 3
    pos_top_3= pd.DataFrame(Top3_good)
    Positive_Top_3_review = []
    for i in range(len(pos_top_3)):
        good_top = {
        'grade':i+1,
        'score':round(pos_top_3.loc[i,1], 2),
        'review':pos_top_3.loc[i,2],
        }
        Positive_Top_3_review.append(good_top)

    
    # 부정 Top 3
    neg_top_3= pd.DataFrame(Top3_bad)
    Negative_Top_3_review = []
    for i in range(len(neg_top_3)):
        good_top = {
        'grade':i+1,
        'score':round(neg_top_3.loc[i,1], 2),
        'review':neg_top_3.loc[i,2],
        }
        Negative_Top_3_review.append(good_top)

    return render_template('modal.html',                          
                            shoplink = plink, 
                            product_data = product_info,
                            # pos_review = pos_review,
                            # neg_review = neg_review,
                            good_text=good_text,
                            bad_text=bad_text,
                            suggest_list = recommended_product_list,
                            bar_count = bar_cnt,
                            donut_per = donut_per,
                            Positive_Top_3_review = Positive_Top_3_review,
                            Negative_Top_3_review = Negative_Top_3_review)

# 전체 리뷰 페이지
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

# 별점 1점
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

# 별점 2점
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

# 별점 3점
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

# 별점 4점
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

# 별점 5점
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



if __name__ == '__main__':
    app.run()


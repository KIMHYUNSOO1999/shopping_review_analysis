# 다나와 제품리스트 크롤링
from selenium import webdriver
# 추가로 by import 해야 함
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
import time
import csv

# window 브라우저 생성
browser = webdriver.Chrome('C:/chromedriver.exe') 
# mac일때 /User/mac user name../Documents/chromedriver

# 사이트 열기
browser.get('https://www.danawa.com')

# 로딩이 끝날때까지 10초간 기다리기
browser.implicitly_wait(10)

# # 쇼핑메뉴 클릭
# browser.find_element(By.CLASS_NAME, 'shop').click()
# #클릭 후 2초간 기다리기, time import 후 사용하기
# time.sleep(2)

# 검색창 클릭
search = browser.find_element(By.CLASS_NAME, 'search__input') #search_area_content
search.click()

# 검색어 입력
search.send_keys('김치')
# enter 치는 명령어
search.send_keys(Keys.ENTER)

# 무한 스크롤로 상품 최대한 많이 가져오기
# 스크롤 전 높이, execute_script: 자바스크립트 실행 명령어
before_h = browser.execute_script('return window.scrollY')
# 무한 스크롤 
while True:
    #맨 아래로 스크롤을 내린다. - 키보드의 END(화살표 위) 실행
    browser.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.END)
    # 스크롤 사이 페이지 로딩 시간 추가 
    time.sleep(1)
    after_h = browser.execute_script('return window.scrollY')
    if after_h == before_h:
        break
    before_h = after_h

# 파일 생성 - 경로, 쓰기 모드, 인코딩, newline='' window에서 들어가는 자동 줄바꿈 문자 없애기
f = open(r'C:\Users\hkPark\팀프로젝트\Danawa_Productlist.csv', 'w',encoding= 'CP949', newline='')
cssWriter = csv.writer(f)

#상품 찾아오기
items = browser.find_elements(By.CSS_SELECTOR, '.prod_main_info')
#items2 = browser.find_elements(By.CSS_SELECTOR, '.rank_one') #.prod_pricelist
for item in items:
    name = item.find_element(By.CSS_SELECTOR, '.prod_name > a').text
    try:
        price = item.find_element(By.CSS_SELECTOR, '.price_sect > a').text#p.price_sect > a > strong
    except:
        price = '출시예정'
    link = item.find_element(By.CSS_SELECTOR, '.prod_name > a').get_attribute('href')
    print(name, price, link)
    # 데이터 쓰기
    cssWriter.writerow([name, price, link])


# 파일 닫기
f.close()
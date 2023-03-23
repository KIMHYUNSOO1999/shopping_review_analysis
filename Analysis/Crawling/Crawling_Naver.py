from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

url="https://smartstore.naver.com/palgongkimchi/products/5318728962?n_media=11068&n_query=%EA%B9%80%EC%B9%98&n_rank=1&n_ad_group=grp-a001-02-000000019287564&n_ad=nad-a001-02-000000119424795&n_campaign_type=2&n_mall_id=ncp_1nr0l8_01&n_mall_pid=5318728962&n_ad_group_type=2"

options = Options()

options = webdriver.ChromeOptions()

options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument('lang=ko_KR')
options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=options) 


driver.implicitly_wait(5)
 
driver.set_window_size(1920,1280)
 
driver.get(url)

a=driver.find_elements(By.CLASS_NAME,"_3QDEeS6NLn")

a1=[]
b1=[]
c1=[]
d1=[]

for i in range(0,len(a),4):
    a1.append(a[i].text)
for i in range(1,len(a),4):
    b1.append(a[i].text)
for i in range(2,len(a),4):
    c1.append(a[i].text)
for i in range(3,len(a),4):
    d1.append(a[i].text)
    
df=pd.DataFrame({'NAME':a1,'DATE':b1,'PRODUCT':c1,'TEXT':d1})

df.to_csv("./Crawling/naver.csv")
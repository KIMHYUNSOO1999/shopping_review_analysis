from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from tqdm import tqdm


def Crawling(url):
    options = Options()

    options = webdriver.ChromeOptions()

    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('lang=ko_KR')
    options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')

    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=options) 


    driver.implicitly_wait(5)
    
    driver.set_window_size(1920,1280)
    
    driver.get(url)

    row_text=[]

    for i in tqdm(range(10)):
        
        pages=driver.find_elements(By.CLASS_NAME,"page_num")

        if i==0:
            
            res=driver.find_elements(By.CLASS_NAME,"atc")

            for row in res:
                row_text.append(row.text)
            
        else:
            
            page_Btn=pages[i].get_attribute('id')
            
            time.sleep(0.5)
            
            BTN=driver.find_element(By.ID,page_Btn)
            
            BTN.click()
            
            time.sleep(0.5)
            
            res=driver.find_elements(By.CLASS_NAME,"atc")

            for row in res:
                row_text.append(row.text)   
                
                

        df=pd.DataFrame({'text':row_text})

        df.to_csv("./Crawling/danawa.csv")
        
        
if __name__=="__main__":
    
    url="https://prod.danawa.com/info/?pcode=10943649&keyword=%EA%B9%80%EC%B9%98&cate=1622479#bookmark_cm_opinion"
    Crawling(url)
    
        

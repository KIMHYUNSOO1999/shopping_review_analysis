import asyncio
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import aiohttp


async def fetch(session, url):

    async with session.get(url) as response:


        df_dic = {}
        df_dic['review'] = []
        df_dic['mall'] = []
        df_dic['date'] = []
        df_dic['name'] = []
        df_dic['star_score'] = []
        df_dic['label'] = []

        html =  await response.content.read()
        soup = BeautifulSoup(html, 'html.parser') #가져온 문서를 html 객체로 만듦

        item = soup.find_all('li', attrs={'class':'danawa-prodBlog-companyReview-clazz-more'})
        for res in item:

            
            review = res.select_one('.rvw_atc > .atc_cont > .atc').get_text() # 리뷰
            mall = res.find('img')['src'] # 쇼핑몰 로고
            date = res.select_one('.date').get_text() # 리뷰 작성 날짜
            name = res.select_one('.name').get_text() # 작성자 아이디(이름)
            star_score = int(res.select_one('.star_mask').get_text().replace("점", "")) # 별점 0, 20, 40, 60, 80, 100


            if int(star_score) >= 80:
                label = 1 
            elif int(star_score) <= 40:
                label = 0
            else:
                label=2

            df_dic['review'].append(review)
            df_dic['mall'].append(mall)
            df_dic['date'].append(date)
            df_dic['name'].append(name)
            df_dic['star_score'].append(star_score)
            df_dic['label'].append(label)

    return df_dic

async def get_reviews(url, prodCode):
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

    res = requests.get(url,headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser') 

    count = soup.select_one('#danawa-prodBlog-companyReview-button-tab-companyReview > strong').get_text() 
    review_page = round(int(count.replace(',', '')) / 10)  

    urls = []
    for i in range(1, review_page+1):
        url2 = "https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=" + prodCode + "&cate1Code=861&page=" + str(i)
        urls.append(url2)
        
    connector = aiohttp.TCPConnector(force_close=True,limit=60)
    async with aiohttp.ClientSession(connector=connector) as session:
        result = await asyncio.gather(*[fetch(session, url) for url in urls])

    return result

def Crawling_async(url,prodCode):
    start = time.time()

    answer= asyncio.run(get_reviews(url,prodCode))

    df=pd.DataFrame()

    for i in range(len(answer)):
        tmp = pd.DataFrame(answer[i])
        df=pd.concat([df,tmp])

    df=df.reset_index()
    del df['index']

    dict_from_df = df.to_dict('records')
    end = time.time()
    
    print(end-start)

    return dict_from_df

prodCode='11057175'
url='https://prod.danawa.com/info/dpg/ajax/companyProductReview.ajax.php?t=0.24477360207876253&prodCode=11057175&cate1Code=861&page=1'
df=Crawling_async(url,prodCode)
print(df)
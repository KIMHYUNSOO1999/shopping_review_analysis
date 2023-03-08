import requests
import re
from bs4 import BeautifulSoup

def get_link(product_name):
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

    return value
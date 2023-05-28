import pandas as pd
from konlpy.tag import Mecab
from collections import Counter
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt 
import matplotlib 
from IPython.display import set_matplotlib_formats 
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS

matplotlib.rc('font',family = 'Malgun Gothic') 
set_matplotlib_formats('retina') 
matplotlib.rc('axes',unicode_minus = False)

mecab = Mecab()

def wordcloud_png(df):
    df=pd.read_csv('C:/Users/KHS/Desktop/대학교/토이 프로젝트/shopping_review_analysis/Analysis/Csv/danawa2_label.csv',encoding='CP949')
    
    good_text=[]
    bad_text=[]

    for i in range(len(df)):
        if df.loc[i,'label']==1:
            good_text.append(df.loc[i,'text'])
        else:
            bad_text.append(df.loc[i,'text'])
            
    good_text = [x for x in good_text if pd.isnull(x) == False]
    bad_text = [x for x in bad_text if pd.isnull(x) == False]
    
    good_morphs = []
    bad_morphs = []

    for i in range(len(good_text)):
        try:
            good_morphs.append(mecab.pos(good_text[i]))
        except UnicodeDecodeError:
            pass

    for i in range(len(bad_text)):
        try:
            bad_morphs.append(mecab.pos(bad_text[i]))
        except UnicodeDecodeError:
            pass
        
    good_list=[] 
    bad_list=[] 

    for sentence in good_morphs : 
        for word, tag in sentence : 
            if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA"] and ("것" not in word) and ("내" not in word)and ("나" not in word)and ("수"not in word) and("게"not in word)and("말"not in word)and("좋"not in word):
                good_list.append(word)

    for sentence in bad_morphs : 
        for word, tag in sentence : 
            if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA"] and ("것" not in word) and ("내" not in word)and ("나" not in word)and ("수"not in word) and("게"not in word)and("말"not in word)and("좋"not in word):
                bad_list.append(word)

    good_count = Counter(good_list)
    good_word = dict(good_count.most_common())

    bad_count = Counter(bad_list)
    bad_word = dict(bad_count.most_common())
    
    alice_coloring = np.array(Image.open('C:/Users/KHS/Desktop/대학교/토이 프로젝트/shopping_review_analysis/Processing/cloud_image.png'))
    stopwords = set(STOPWORDS)
    stopwords.add("said")
    wc = WordCloud(font_path = '/content/Binggrae_0.ttf', background_color='white',colormap = "inferno",mask=alice_coloring,width=1500, height=1000)
    
    wc.generate_from_frequencies(good_word)
    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(8, 6)
    plt.axis('off') 
    plt.savefig('C:/Users/KHS/Desktop/대학교/토이 프로젝트/shopping_review_analysis/Flask/static/image/good_wordcloud.png')
    
    wc.generate_from_frequencies(bad_word)
    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(8, 6)
    plt.axis('off') 
    plt.savefig('C:/Users/KHS/Desktop/대학교/토이 프로젝트/shopping_review_analysis/Flask/static/image/bad_wordcloud.png')
     
if __name__=="__main__":
    df=pd.read_csv('C:/Users/KHS/Desktop/대학교/토이 프로젝트/shopping_review_analysis/Processing/danawa2_label.csv',encoding='CP949')
    wordcloud_png(df)
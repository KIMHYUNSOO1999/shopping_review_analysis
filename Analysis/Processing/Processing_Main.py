import pandas as pd
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow_addons.optimizers import RectifiedAdam
import time
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import seaborn as sns
import matplotlib 
from IPython.display import set_matplotlib_formats 
from konlpy.tag import Okt,Mecab
from textrank import KeysentenceSummarizer
import ayncio
import warnings
import re

warnings.filterwarnings('ignore')

okt = Okt()
mecab = Mecab()

MODEL_NAME = "klue/bert-base"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

model  = tf.keras.models.load_model('/content/drive/MyDrive/halla/best_model.h5'
                ,custom_objects={'TFBertForSequenceClassification': TFBertForSequenceClassification})

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
def Processing_classification(df):


    import warnings
    warnings.filterwarnings('ignore')
    
    stop_word=set()
    with open("C:/Users/KHS/Desktop/stop_word.txt", "r",encoding="UTF-8") as f:
        for line in f:
            stop_word.add(line.strip())
            
    for word in stop_word:
        df['review'] = df['review'].str.replace(word," ")
            
    df['review'] = df['review'].str.replace(r"[a-zA-Z]"," ")
    df['review'] = df['review'].str.replace(r"[^가-힣]"," ")
    df['review'] = df['review'].str.replace(r"\s+"," ")
    df['review'] = df['review'].str.strip()
    
    df = df[df['review'].str.strip().astype(bool)]
    df = df.reset_index(drop=True)
    
    X_data = df['review']
    MAX_SEQ_LEN = 80
    tokenizer = BertTokenizer.from_pretrained('klue/bert-base')

    # train 데이터를 Bert의 Input 타입에 맞게 변환

    train_x= convert_data(X_data,MAX_SEQ_LEN,tokenizer)

    # print(train_x)
    predicted_value = model.predict(train_x)
    predicted_label = np.argmax(predicted_value, axis = 1)
    
    df['quarter']=0
    df['year']=0
    df['month']=0
    
    df=df.reset_index()
    
    for i in range(len(df)):

        df.loc[i,'year']=df.loc[i,'date'].split('.')[0]
        df.loc[i,'month']=df.loc[i,'date'].split('.')[1]

        tmp=df.loc[i,'date'].split('.')[1]
    
        if tmp=='01'or tmp=='02' or tmp=='03':
            df.loc[i,'quarter']=1
        elif tmp=='04'or tmp=='05' or tmp=='06':
            df.loc[i,'quarter']=2
        elif tmp=='07'or tmp=='08' or tmp=='09':
            df.loc[i,'quarter']=3
        else:
            df.loc[i,'quarter']=4

        if df.loc[i,'star_score']==100:
            df.loc[i,'star_score']=4
        elif df.loc[i,'star_score']==80:
            df.loc[i,'star_score']=3
        elif df.loc[i,'star_score']==60:
            df.loc[i,'star_score']=2
        elif df.loc[i,'star_score']==40:
            df.loc[i,'star_score']=1
        else:
            df.loc[i,'star_score']=0

    data = {
    'text':df['review'],
    'year':df['year'],
    'quarter':df['quarter'],
    'month':df['month'],
    'label_old':df['star_score'],
    'label_new':predicted_label
    }
 
    df_final = pd.DataFrame(data)
    
    print("감정분석 종료")
    return df_final

def Processing_OKT(df):  

    good_text=[]
    bad_text=[]

    df.reset_index(inplace=True)

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

    matplotlib.rc('font',family = 'Malgun Gothic') 
    set_matplotlib_formats('retina') 
    matplotlib.rc('axes',unicode_minus = False)

    max = 200
    good_top = {}
    bad_top = {}

    for word, counts in good_count.most_common(max):
        good_top[word] = counts 

    for word, counts in bad_count.most_common(max):
        bad_top[word] = counts  

    alice_coloring = np.array(Image.open('/content/drive/MyDrive/halla/cloud_image.png'))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(font_path = '/content/drive/MyDrive/halla/Binggrae_0.ttf', background_color='white',colormap = "YlOrRd",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(good_top)

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('/content/drive/MyDrive/halla/cloud_image1.png', bbox_inches='tight')

    wc = WordCloud(font_path = '/content/drive/MyDrive/halla/Binggrae_0.ttf', background_color='white',colormap = "plasma",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(bad_top) 

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('/content/drive/MyDrive/halla/cloud_image2.png', bbox_inches='tight')

    plt.clf()

    print("워드클라우드 종료")
    
    
async def Processing_Mecab(df):  

    good_text=[]
    bad_text=[]

    df.reset_index(inplace=True)

    for i in range(len(df)):
        if df.loc[i,'label_new']==1:
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
    stopwords = ['이', '있', '하', '것', '들', '그', '되', '수', '이', '보', '않', '없', '나', '사람', '주', '아니', '등', '같', '우리', '때', '년', '가', '한', '지', '대하', '오', '말', '일', '그렇', '위하','거','듯','데']
    for sentence in good_morphs : 
        for word, tag in sentence : 
            if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA","VCP"] and (word not in stopwords) and len(word)>1:
                    good_list.append(word)

    for sentence in bad_morphs : 
        for word, tag in sentence : 
            if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA","VCN"] and (word not in stopwords) and len(word)>1:
                    bad_list.append(word)
        
    good_count = Counter(good_list)
    good_word = dict(good_count.most_common())

    bad_count = Counter(bad_list)
    bad_word = dict(bad_count.most_common())

    matplotlib.rc('font',family = 'Malgun Gothic') 
    set_matplotlib_formats('retina') 
    matplotlib.rc('axes',unicode_minus = False)

    max = 200
    good_top = {}
    bad_top = {}

    for word, counts in good_count.most_common(max):
        good_top[word] = counts 

    for word, counts in bad_count.most_common(max):
        bad_top[word] = counts  

    alice_coloring = np.array(Image.open('/content/drive/MyDrive/halla/cloud_image.png'))
    stopwords = set(STOPWORDS)
    stopwords.add("said")

    wc = WordCloud(font_path = '/content/drive/MyDrive/halla/Binggrae_0.ttf', background_color='white',colormap = "YlOrRd",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(good_top)

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('/content/drive/MyDrive/halla/cloud_image1.png', bbox_inches='tight')

    wc = WordCloud(font_path = '/content/drive/MyDrive/halla/Binggrae_0.ttf', background_color='white',colormap = "plasma",mask=alice_coloring,width=1500, height=1500)
    wc.generate_from_frequencies(bad_top) 

    plt.imshow(wc)
    figure = plt.gcf() 
    figure.set_size_inches(15, 15)
    plt.axis('off') 
    plt.savefig('/content/drive/MyDrive/halla/cloud_image2.png', bbox_inches='tight')

    plt.clf()

    print("워드클라우드 종료")
    
    
def Mecab_tokenizer(sent):
    words = mecab.pos(sent, join=True)
    words = [w for w in words if ('NNP' in w  or 'NNG' in w,'NA' in w  or 'VA' in w,'NNB' in w  or 'MM' in w,'IC' in w  or 'MA' in w,'VCN' in w)]
    
    return words

async def Processing_TextRank(df):

    df=df.dropna(axis=0)

    good_text=[]
    bad_text=[]
    
    for i in range(len(df)):
        if df.loc[i,'label_new']==1:
            good_text.append(df.loc[i,'text'])
        else:
            bad_text.append(df.loc[i,'text'])


    summarizer = KeysentenceSummarizer(tokenize = Mecab_tokenizer, min_sim = 0.6)
    keysents_good = summarizer.summarize(good_text, topk=3)
    keysents_bad= summarizer.summarize(bad_text, topk=3)

    print("텍스트링크 종료")
    
    return keysents_good,keysents_bad

async def Processing_Graph(df):
    df_group1 = df.groupby(['year', 'quarter'])['label_new'].apply(lambda x: pd.Series([(x == 0).sum(), (x == 1).sum()])).reset_index()
    df_group1.rename(columns={'level_2':'PN','label_new':'value'},inplace=True)

    df_1=df.groupby(['year','quarter']).count().reset_index()
    df_1.rename(columns={'label_new':'value'},inplace=True)

    del df_1['text']
    del df_1['month']
    del df_1['label_old']

    sns.set_theme(style="ticks")
    plt.title('All Year&Qauter review', fontsize=14)
    sns.set(rc = {'figure.figsize':(15,15)})
    ax=sns.barplot(data=df_1,x='year',y='value',hue='quarter',ci=None)
    ax.legend(['Q1','Q2','Q3','Q4'],loc='upper right')
    plt.savefig('image1.png')

    df_2=df_group1.groupby(['year','PN']).sum().reset_index()
    del df_2['quarter']
    
    plt.clf()
    sns.set_theme(style="ticks")
    plt.title('All Year&Qauter Positive/Negative', fontsize=14)
    sns.set(rc = {'figure.figsize':(8,8)})
    ax=sns.barplot(data=df_2,x='year',y='value',hue='PN',ci=None)
    ax.legend(['Negative','Positive'],loc='upper right')
    plt.savefig('image2.png')

    df_3=df_group1.groupby('year').sum().reset_index()
    df_3

    plt.clf()
    sns.set(rc = {'figure.figsize':(8,8)})
    sns.set_theme(style="ticks")
    plt.title('All Year Reiview', fontsize=14)
    ax=sns.barplot(data=df_3,x='year',y='value',ci=None)
    plt.savefig('image3.png')


async def Processing_async(df):

    await Processing_Mecab(df)
    await Processing_Graph(df)
    Top3_good,Top3_bad=  await Processing_TextRank(df)

    return Top3_good,Top3_bad

def Prcessing_main():
    
    df=pd.read_csv('/content/drive/MyDrive/halla/danawa2.csv')
    df=df.dropna(axis=0)

    start_time = time.time()

    df_one=Processing_classification(df)

    Top3_good,Top3_bad=asyncio.run(Processing_async(df_one))

    end_time = time.time()

    print(end_time-start_time)

Prcessing_main()

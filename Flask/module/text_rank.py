# from eunjeon import Mecab
from konlpy.tag import Mecab
import time
import pandas as pd
from textrank import KeysentenceSummarizer
from module import mecab_wordcloud, run_model

import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow_addons.optimizers import RectifiedAdam
# from app import model

tf.keras.optimizers.RectifiedAdam = RectifiedAdam
# mecab = Mecab("C:/mecab/mecab-ko-dic")

def text_rank(good_text, bad_text):
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
  
  return pos_review, neg_review

# def convert_data(X_data,MAX_SEQ_LEN,tokenizer):
#   # BERT 입력으로 들어가는 token, mask, segment, target 저장용 리스트
#   tokens, masks, segments, targets = [], [], [], []
  
#   for X in (X_data):
#       # token: 입력 문장 토큰화
#       token = tokenizer.encode(X, truncation = True, padding = 'max_length', max_length = MAX_SEQ_LEN)
      
#       # Mask: 토큰화한 문장 내 패딩이 아닌 경우 1, 패딩인 경우 0으로 초기화
#       num_zeros = token.count(0)
#       mask = [1] * (MAX_SEQ_LEN - num_zeros) + [0] * num_zeros
      
#       # segment: 문장 전후관계 구분: 오직 한 문장이므로 모두 0으로 초기화
#       segment = [0]*MAX_SEQ_LEN

#       tokens.append(token)
#       masks.append(mask)
#       segments.append(segment)

#   # numpy array로 저장
#   tokens = np.array(tokens)
#   masks = np.array(masks)
#   segments = np.array(segments)

#   return [tokens, masks, segments]

# # 최고 성능의 모델 불러오기
# def Processing_classification(df):
#   import warnings
#   warnings.filterwarnings('ignore')

# #   from pathlib import Path
# #   BASE_DIR = Path(__file__).resolve().parent.parent
# #   df = pd.read_csv(BASE_DIR/'danawa.csv')
#   # df = df.drop('Unnamed: 0',axis= 1)

#   df['review'] = df['review'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
#   df['review'].nunique()
#   df.drop_duplicates(subset=['review'], inplace=True)

#   X_data = df['review']
#   MAX_SEQ_LEN = 80
#   tokenizer = BertTokenizer.from_pretrained('klue/bert-base')

#   # train 데이터를 Bert의 Input 타입에 맞게 변환

#   train_x= convert_data(X_data,MAX_SEQ_LEN,tokenizer)

#   # print(train_x)
#   predicted_value = model.predict(train_x)
#   predicted_label = np.argmax(predicted_value, axis = 1)

#   global label_review

#   data = {
#       'review':df['review'],
#       'mall_logo':df['mall_logo'],
#       'date':df['date'],
#       'name':df['name'],
#       'star_score':df['star_score'],
#       'label':predicted_label
#   }

#   df_final = pd.DataFrame(data)
#   df_final.to_csv('danawa_label.csv',encoding='CP949')

#   label_review = df_final.to_dict('records') # df를 딕셔너리 변환해서 사용

#   # 긍부정 단어 퍼센트
#   global pos_per, neg_per
#   total = df_final['label'].count()
#   pos_count = df_final[df_final['label']==1].label.count() 
#   neg_count = df_final[df_final['label']==0].label.count() 

#   pos_per = round((pos_count / total)*100, 2)
#   neg_per = round((neg_count / total)*100, 2)

#   # 별점 별 개수
#   global five_count, four_count, three_count, two_count, one_count, zero_count
#   five_count = df_final[df_final['star_score']==100].star_score.count() 
#   four_count = df_final[df_final['star_score']==80].star_score.count() 
#   three_count = df_final[df_final['star_score']==60].star_score.count() 
#   two_count = df_final[df_final['star_score']==40].star_score.count() 
#   one_count = df_final[df_final['star_score']==20].star_score.count() 
#   zero_count = df_final[df_final['star_score']==0].star_score.count() 

#   # 긍정, 부정 리뷰 리스트로 분리
#   global good_text, bad_text
#   good_text=[]
#   bad_text=[]
  
#   # print(len(df_final))
#   df_final.reset_index(inplace=True)
#   for i in range(len(df_final)):
      
#       if df_final.loc[i,'label']==1:
#           good = {
#               'review':df_final.loc[i,'review'],
#               'mall_logo':df_final.loc[i,'mall_logo'],
#               'date':df_final.loc[i,'date'],
#               'name':df_final.loc[i,'name'],
#               'star_score':df_final.loc[i,'star_score'],
#               'label':df_final.loc[i,'label']
#           }
#           good_text.append(good)
#       else:
#           bad = {
#               'review':df_final.loc[i,'review'],
#               'mall_logo':df_final.loc[i,'mall_logo'],
#               'date':df_final.loc[i,'date'],
#               'name':df_final.loc[i,'name'],
#               'star_score':df_final.loc[i,'star_score'],
#               'label':df_final.loc[i,'label']
#           }
#           bad_text.append(bad)
#       # except:
#       #     print(i)
#       #     pass

#   return good_text, bad_text, pos_per, neg_per, label_review, five_count, four_count, three_count, two_count, one_count, zero_count

# def Mecab_tokenizer(sent):
#     words = mecab.pos(sent, join=True)
#     words = [w for w in words if ('NNP' in w  or 'NNG' in w,'NA' in w  or 'VA' in w,'NNB' in w  or 'MM' in w,'IC' in w  or 'MA' in w,'VCN' in w)]
    
#     return words

# def Processing_TextRank(df):

#     df=df.dropna(axis=0)

#     good_text=[]
#     bad_text=[]

#     df.reset_index(inplace=True)
    
#     for i in range(len(df)):
#         if df.loc[i,'label']==1:
#             good_text.append(df.loc[i,'text'])
#         else:
#             bad_text.append(df.loc[i,'text'])

#     for i in good_text:

#         i=i.strip()

#         if ('https:'in str(i)) or (str(i).rstrip()==''):
#             good_text.remove(i)
#         elif '\r\n\r\n' in i:
#             good_text[good_text.index(i)]=i.replace('\r\n\r\n','')

#     for i in bad_text:

#         i=i.strip()

#         if ('https:' in str(i)) or (str(i).rstrip()==''):
#             bad_text.remove(i)
#         elif '\r\n\r\n' in i:
#             bad_text[bad_text.index(i)]=i.replace('\r\n\r\n','')

#     summarizer = KeysentenceSummarizer(tokenize = Mecab_tokenizer, min_sim = 0.6)
#     keysents_good = summarizer.summarize(good_text, topk=3)
#     keysents_bad= summarizer.summarize(bad_text, topk=3)
#     print(keysents_good)

#     print("텍스트랭크 종료")
    
#     return keysents_good,keysents_bad



# def Prcessing_main():
    
#     df=pd.read_csv('danawa.csv')
#     df=df.dropna(axis=0)

#     start_time = time.time()

#     df_one=Processing_classification(df)
#     # Processing_OKT(df_one)
#     mecab_wordcloud.Processing_Mecab(df_one)
#     Top3_good,Top3_bad=Processing_TextRank(df_one)

#     end_time = time.time()

#     print(end_time-start_time)
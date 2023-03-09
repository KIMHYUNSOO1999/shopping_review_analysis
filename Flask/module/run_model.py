import pandas as pd
import numpy as np
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow_addons.optimizers import RectifiedAdam
from app import model

tf.keras.optimizers.RectifiedAdam = RectifiedAdam

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
  BASE_DIR = Path(__file__).resolve().parent.parent
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
  
  # print(len(df_final))
  df_final.reset_index(inplace=True)
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
      # except:
      #     print(i)
      #     pass

  return good_text, bad_text, pos_per, neg_per, label_review, five_count, four_count, three_count, two_count, one_count, zero_count
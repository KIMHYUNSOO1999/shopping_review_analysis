import pandas as pd
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification


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

    MODEL_NAME = "klue/bert-base"
    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

    model  = tf.keras.models.load_model(BASE_DIR/'model/best_model.h5',
                                                      custom_objects={'TFBertForSequenceClassification': TFBertForSequenceClassification})

    df = pd.read_csv(BASE_DIR/'Processing/danawa2.csv')
      
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
    
    data = {
    'text':df['review'],
    'label':predicted_label
    }
 
    df_final = pd.DataFrame(data)
    
    df_final.to_csv(BASE_DIR/'Processing/danawa2_label.csv',encoding='CP949')



get_title_score2()



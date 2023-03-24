from eunjeon import Mecab
# from konlpy.tag import Mecab
from textrank import KeysentenceSummarizer
import pandas as pd
import asyncio

# mecab = Mecab(dicpath="C:/mecab/mecab-ko-dic")
mecab = Mecab()
def Mecab_tokenizer(sent):
    # words = mecab.pos(sent, join=True)
    words = mecab.pos(sent)
    words = [w for w in words if ('NNP' in w  or 'NNG' in w,'NA' in w  or 'VA' in w,'NNB' in w  or 'MM' in w,'IC' in w  or 'MA' in w,'VCN' in w)]
    
    return words

async def Processing_TextRank(df_one):


    good_text=[]
    bad_text=[]

    df_one.reset_index(inplace=True)
    
    for i in range(len(df_one)):
        if df_one.loc[i,'label']==1:
            good_text.append(df_one.loc[i,'text'])
        else:
            bad_text.append(df_one.loc[i,'text'])

    for i in good_text:

        i=i.strip()

        if ('https:'in str(i)) or (str(i).rstrip()==''):
            try:
                good_text.remove(i)
            except:
                pass
        elif '\r\n\r\n' in i:
            good_text[good_text.index(i)]=i.replace('\r\n\r\n','')

    for i in bad_text:

        i=i.strip()

        if ('https:' in str(i)) or (str(i).rstrip()==''):
            try:
                bad_text.remove(i)
            except:
                pass
        elif '\r\n\r\n' in i:
            bad_text[bad_text.index(i)]=i.replace('\r\n\r\n','')

    summarizer = KeysentenceSummarizer(tokenize = Mecab_tokenizer, min_sim = 0.6)
    keysents_good = summarizer.summarize(good_text, topk=3)
    keysents_bad= summarizer.summarize(bad_text, topk=3)

    print("텍스트랭크 종료")
    
    return keysents_good,keysents_bad

# Processing_TextRank()
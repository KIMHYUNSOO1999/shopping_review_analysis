from konlpy.tag import Okt   
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 
from IPython.display import set_matplotlib_formats 
from eunjeon import Mecab
# from konlpy.tag import Mecab

mecab = Mecab()

def Processing_Mecab():
  good_text=[]
  bad_text=[]
  df2 = pd.read_csv('danawa_label.csv', encoding='CP949')
  df3 = df2.dropna(axis=0)
  df3.reset_index(inplace=True)
  

  for i in range(len(df3)):
    if df3.loc[i,'label']==1:
        good_text.append(df3.loc[i,'review'])
    else:
        bad_text.append(df3.loc[i,'review'])



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
          if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA","VCP"] and ("것" not in word) and ("내" not in word)and ("나" not in word)and ("수"not in word) and("게"not in word)and("말"not in word)and("좋"not in word):
              good_list.append(word)

  for sentence in bad_morphs : 
      for word, tag in sentence : 
          if tag in ['NNP',"NNG","NA","VA","NNB","VA","MM","IC","MA","VCN"] and ("것" not in word) and ("내" not in word)and ("나" not in word)and ("수"not in word) and("게"not in word)and("말"not in word)and("좋"not in word):
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

  alice_coloring = np.array(Image.open('static/image/cloud_image.png'))
  stopwords = set(STOPWORDS)
  stopwords.add("said")

  wc = WordCloud(font_path = 'font/BinggraeⅡ-Bold.ttf', background_color='white',colormap = "YlOrRd",mask=alice_coloring,width=1500, height=1500)
  wc.generate_from_frequencies(good_top)

  plt.imshow(wc)
  figure = plt.gcf() 
  figure.set_size_inches(15, 15)
  plt.axis('off') 
  plt.savefig('static/image/pos_wordcloud.png', bbox_inches='tight')

  wc = WordCloud(font_path = 'font/BinggraeⅡ-Bold.ttf', background_color='white',colormap = "plasma",mask=alice_coloring,width=1500, height=1500)
  wc.generate_from_frequencies(bad_top) 

  plt.imshow(wc)
  figure = plt.gcf() 
  figure.set_size_inches(15, 15)
  plt.axis('off') 
  plt.savefig('static/image/neg_wordcloud.png', bbox_inches='tight')

  plt.clf()

  print("워드클라우드 종료")
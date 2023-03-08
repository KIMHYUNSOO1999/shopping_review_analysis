from konlpy.tag import Okt   
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import numpy as np

def wordcloud():  
  okt = Okt()

  df2 = pd.read_csv('danawa_label.csv', encoding='CP949')
  del df2['Unnamed: 0']
  good_text=[]
  bad_text=[]

  for i in range(len(df2)):
      if df2.loc[i,'label']==1:
          good_text.append(df2.loc[i,'review'])
      else:
          bad_text.append(df2.loc[i,'review'])

  good_text = [x for x in good_text if pd.isnull(x) == False]
  bad_text = [x for x in bad_text if pd.isnull(x) == False]

  okt = Okt()

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

  import matplotlib 
  from IPython.display import set_matplotlib_formats 
  matplotlib.rc('font',family = 'Malgun Gothic') 
  set_matplotlib_formats('retina') 
  matplotlib.rc('axes',unicode_minus = False)

  max = 100
  good_top = {}
  bad_top = {}

  for word, counts in good_count.most_common(max):
      good_top[word] = counts 

  for word, counts in bad_count.most_common(max):
      bad_top[word] = counts  

  # 긍정 워드 클라우드
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

  # 부정 워드 클라우드
  alice_coloring = np.array(Image.open('static/image/cloud_image.png'))
  stopwords = set(STOPWORDS)
  stopwords.add("said")

  wc = WordCloud(font_path = 'font/BinggraeⅡ-Bold.ttf', background_color='white',colormap = "plasma",mask=alice_coloring,width=1500, height=1500)
  wc.generate_from_frequencies(bad_top) 

  plt.imshow(wc)
  figure = plt.gcf() 
  figure.set_size_inches(15, 15)
  plt.axis('off') 
  plt.savefig('static/image/neg_wordcloud.png', bbox_inches='tight')
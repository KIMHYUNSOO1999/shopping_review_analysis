import pandas as pd
import numpy as np

async def year_quarter_cnt():
  df = pd.read_csv('danawa_label.csv', encoding='CP949')

  new_df = df.dropna(axis=0)
  new_df.reset_index(inplace=True)

  year_quarter_df = new_df.copy()
  year_quarter_df['quarter']=0
  year_quarter_df['year']=0

  for i in range(len(year_quarter_df)):
    year_quarter_df.loc[i,'year']=year_quarter_df.loc[i,'date'].split('.')[0]
    tmp=year_quarter_df.loc[i,'date'].split('.')[1]
    
    if tmp=='01'or tmp=='02' or tmp=='03':
        year_quarter_df.loc[i,'quarter']=1
    elif tmp=='04'or tmp=='05' or tmp=='06':
        year_quarter_df.loc[i,'quarter']=2
    elif tmp=='07'or tmp=='08' or tmp=='09':
        year_quarter_df.loc[i,'quarter']=3
    else:
        year_quarter_df.loc[i,'quarter']=4
  
  # 2023년 분기별 긍부정 리뷰 카운트
  firstQuarter_pos_cnt23 = 0
  firstQuarter_neg_cnt23 = 0

  secondQuarter_pos_cnt23 = 0
  secondQuarter_neg_cnt23 = 0

  thirdQuarter_pos_cnt23 = 0
  thirdQuarter_neg_cnt23 = 0

  fourthQuarter_pos_cnt23 = 0
  fourthQuarter_neg_cnt23 = 0
  # 2022년 분기별 긍부정 리뷰 카운트
  firstQuarter_pos_cnt22 = 0
  firstQuarter_neg_cnt22 = 0

  secondQuarter_pos_cnt22 = 0
  secondQuarter_neg_cnt22 = 0

  thirdQuarter_pos_cnt22 = 0
  thirdQuarter_neg_cnt22 = 0

  fourthQuarter_pos_cnt22 = 0
  fourthQuarter_neg_cnt22 = 0

  # 2021년 분기별 긍부정 리뷰 카운트
  firstQuarter_pos_cnt21 = 0
  firstQuarter_neg_cnt21 = 0

  secondQuarter_pos_cnt21 = 0
  secondQuarter_neg_cnt21 = 0

  thirdQuarter_pos_cnt21 = 0
  thirdQuarter_neg_cnt21 = 0

  fourthQuarter_pos_cnt21 = 0
  fourthQuarter_neg_cnt21 = 0

  # 2020년 분기별 긍부정 리뷰 카운트
  firstQuarter_pos_cnt20 = 0
  firstQuarter_neg_cnt20 = 0

  secondQuarter_pos_cnt20 = 0
  secondQuarter_neg_cnt20 = 0

  thirdQuarter_pos_cnt20 = 0
  thirdQuarter_neg_cnt20 = 0

  fourthQuarter_pos_cnt20 = 0
  fourthQuarter_neg_cnt20 = 0

  # 기타
  firstQuarter_pos_cnt_other = 0
  firstQuarter_neg_cnt_other = 0

  secondQuarter_pos_cnt_other = 0
  secondQuarter_neg_cnt_other = 0

  thirdQuarter_pos_cnt_other = 0
  thirdQuarter_neg_cnt_other = 0

  fourthQuarter_pos_cnt_other = 0
  fourthQuarter_neg_cnt_other = 0

  for i in range(len(year_quarter_df)):
# 2023년도 -------------------------------------------------------------------------------------------------   
    # 2023년도는 1분기까지밖에 없습니다.
    # 2023년도 1분기 긍정 카운트
    if year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2023' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_pos_cnt23 += 1
    #2023년도 1분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==1:
        firstQuarter_neg_cnt23 += 1
    #2023년도 2분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==2:
        secondQuarter_pos_cnt23 += 1
    #2023년도 2분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==2:
        secondQuarter_neg_cnt23 += 1
    #2023년도 3분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==3:
        secondQuarter_pos_cnt23 += 1
    #2023년도 3분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==3:
        secondQuarter_neg_cnt23 += 1
    #2023년도 4분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==4:
        secondQuarter_pos_cnt23 += 1
    #2023년도 4분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year']=='2023' and year_quarter_df.loc[i, 'quarter']==4:
        secondQuarter_neg_cnt23 += 1
# 2022년도 --------------------------------------------------------------------------------------------    
    #2022년도 1분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_pos_cnt22 += 1
    #2022년도 1분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_neg_cnt22 += 1
    #2022년도 2분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_pos_cnt22 += 1
    #2022년도 2분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_neg_cnt22 += 1
    #2022년도 3분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_pos_cnt22 += 1
    #2022년도 3분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_neg_cnt22 += 1
    #2022년도 4분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter'] == 4:
        fourthQuarter_pos_cnt22 += 1
    #2022년도 4분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2022' and year_quarter_df.loc[i, 'quarter']== 4:
        fourthQuarter_neg_cnt22 += 1
        
#2021년도 ---------------------------------------------------------------------------------------------------
    #2021년도 1분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_pos_cnt21 += 1
    #2021년도 1분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_neg_cnt21 += 1
    #2021년도 2분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_pos_cnt21 += 1
    #2021년도 2분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_neg_cnt21 += 1
    #2021년도 3분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_pos_cnt21 += 1
    #2021년도 3분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_neg_cnt21 += 1
    #2021년도 4분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter'] == 4:
        fourthQuarter_pos_cnt21 += 1
    #2021년도 4분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2021' and year_quarter_df.loc[i, 'quarter']== 4:
        fourthQuarter_neg_cnt21 += 1
        
# 2020 년도 --------------------------------------------------------------------------------------------
    #2020년도 1분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 1:
        firstQuarter_pos_cnt20 += 1
    #2020년도 1분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 1:
         firstQuarter_neg_cnt20 += 1
    #2020년도 2분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_pos_cnt20 += 1
    #2020년도 2분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 2:
        secondQuarter_neg_cnt20 += 1
    #2020년도 3분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_pos_cnt20 += 1
    #2020년도 3분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 3:
        thirdQuarter_neg_cnt20 += 1
    #2020년도 4분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter'] == 4:
        fourthQuarter_pos_cnt20 += 1
    #2020년도 4분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==1 and year_quarter_df.loc[i,'year'] == '2020' and year_quarter_df.loc[i, 'quarter']== 4:
        fourthQuarter_neg_cnt20 += 1

# 나머지 연도 --------------------------------------------------------------------------------------------
    # 나머지 연도 1분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==1:
        firstQuarter_pos_cnt_other += 1
    # 나머지 연도 1분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==1:
        firstQuarter_neg_cnt_other += 1
    # 나머지 연도 2분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==2:
        secondQuarter_pos_cnt_other += 1
    # 나머지 연도 2분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==2:
        secondQuarter_neg_cnt_other += 1
    # 나머지 연도 3분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==3:
        thirdQuarter_pos_cnt_other += 1
    # 나머지 연도 3분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==3:
        thirdQuarter_neg_cnt_other += 1
    # 나머지 연도 4분기 긍정 카운트
    elif year_quarter_df.loc[i,'label']==1 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==4:
        fourthQuarter_pos_cnt_other += 1
    # 나머지 연도 4분기 부정 카운트
    elif year_quarter_df.loc[i,'label']==0 and int(year_quarter_df.loc[i,'year']) < 2020 and year_quarter_df[i, 'quarter']==4:
        fourthQuarter_neg_cnt_other += 1

  return (firstQuarter_pos_cnt23, firstQuarter_neg_cnt23, secondQuarter_pos_cnt23, secondQuarter_neg_cnt23, thirdQuarter_pos_cnt23, thirdQuarter_neg_cnt23, fourthQuarter_pos_cnt23, fourthQuarter_neg_cnt23,
          firstQuarter_pos_cnt22, firstQuarter_neg_cnt22, secondQuarter_pos_cnt22, secondQuarter_neg_cnt22, thirdQuarter_pos_cnt22, thirdQuarter_neg_cnt22, fourthQuarter_pos_cnt22, fourthQuarter_neg_cnt22,
          firstQuarter_pos_cnt21, firstQuarter_neg_cnt21, secondQuarter_pos_cnt21, secondQuarter_neg_cnt21, thirdQuarter_pos_cnt21, thirdQuarter_neg_cnt21, fourthQuarter_pos_cnt21, fourthQuarter_neg_cnt21,
          firstQuarter_pos_cnt20, firstQuarter_neg_cnt20, secondQuarter_pos_cnt20, secondQuarter_neg_cnt20, thirdQuarter_pos_cnt20, thirdQuarter_neg_cnt20, fourthQuarter_pos_cnt20, fourthQuarter_neg_cnt20,
          firstQuarter_pos_cnt_other, firstQuarter_neg_cnt_other, secondQuarter_pos_cnt_other, secondQuarter_neg_cnt_other, thirdQuarter_pos_cnt_other, thirdQuarter_neg_cnt_other, fourthQuarter_pos_cnt_other, fourthQuarter_neg_cnt_other
          )


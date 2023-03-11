import matplotlib.pyplot as plt
import numpy as np

def donut(pos, neg):
    # labels = ['부정 리뷰', '긍정 리뷰']
    # colors = ['#ff9999','#8fd9b6']
    # frequency = [pos, neg]
    # wedgeprops={'width': 0.5}
    # explode = [0.05, 0.00]

    # fig = plt.figure(figsize=(8,8)) 
    # fig.set_facecolor('white') 
    # ax = fig.add_subplot() 

    # pie = ax.pie(frequency, 
    #                 startangle=180, 
    #                 counterclock=False,
    #                 wedgeprops=wedgeprops,
    #                 colors=colors,
    #                 labels=labels,
    #                 explode=explode,
    #                 shadow = True,
    #             )

    # total = np.sum(frequency) ## 빈도수 총합

    # sum_pct = 0 ## 백분율 초기값
    # for i,l in enumerate(labels):
    #     ang1, ang2 = pie[0][i].theta1, pie[0][i].theta2 ## 각1, 각2
    #     r = pie[0][i].r ## 원의 반지름

    #     x = ((r+0.5)/2)*np.cos(np.pi/180*((ang1+ang2)/2)) ## 정중앙 x좌표
    #     y = ((r+0.5)/2)*np.sin(np.pi/180*((ang1+ang2)/2)) ## 정중앙 y좌표

    #     if i < len(labels) - 1:
    #         sum_pct += float(f'{frequency[i]/total*100:.2f}') ## 백분율을 누적한다.
    #         ax.text(x,y,f'{frequency[i]/total*100:.2f}%',ha='center',va='center') ## 백분율 텍스트 표시
    #     else: ## 총합을 100으로 맞추기위해 마지막 백분율은 100에서 백분율 누적값을 빼준다.
    #         ax.text(x,y,f'{100-sum_pct:.2f}%',ha='center',va='center') 

    
    # plt.legend(pie[0],labels) ## 범례 표시
    # plt.rcParams['font.size'] = 15
    # plt.savefig('static/image/donut_chart.png', bbox_inches='tight')

    per = {
        'pos': pos,
        'neg': neg
    }

    return per
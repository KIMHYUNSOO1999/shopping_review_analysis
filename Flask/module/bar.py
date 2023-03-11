import matplotlib.pyplot as plt
import seaborn as sns

def bar(five_count, four_count, three_count, two_count, one_count, zero_count):
    # x = [5, 4, 3, 2, 1, 0]
    # y = [five_count, four_count, three_count, two_count, one_count, zero_count]

    count = {
        'five':five_count,
        'four':four_count,
        'three':three_count,
        'two':two_count,
        'one':one_count,
        'zero':zero_count
    }


    # colors = sns.color_palette('hls',len(y)) # 색상
    # plt.figure(figsize=(10,8))
    # plt.bar(x, y, width=0.7, color=colors, edgecolor='black')
    # plt.xlabel('별점', fontweight = "bold", fontsize=18)
    # plt.ylabel('리뷰 개수', fontweight = "bold", fontsize=18)

    # for i, v in enumerate(x):
    #     plt.text(v, y[i], str(y[i]),
    #             fontsize=18,
    #             color="black",
    #             fontweight = "bold",
    #             horizontalalignment='center',
    #             verticalalignment='bottom')


    return count
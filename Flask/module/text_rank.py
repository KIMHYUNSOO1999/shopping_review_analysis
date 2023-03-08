
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
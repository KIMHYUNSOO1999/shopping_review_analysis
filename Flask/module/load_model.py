from pathlib import Path
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from tensorflow_addons.optimizers import RectifiedAdam
def load_model():
  BASE_DIR = Path(__file__).resolve().parent
  MODEL_NAME = "klue/bert-base"
  tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
  global model
  model  = tf.keras.models.load_model(BASE_DIR/'model/best_model.h5',
                                                      custom_objects={'TFBertForSequenceClassification': TFBertForSequenceClassification})

  return model
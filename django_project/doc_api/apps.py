from django.apps import AppConfig
from tensorflow import keras
import tensorflow_hub as hub

class DocApiConfig(AppConfig):
    name = 'doc_api'
    model = keras.models.load_model('my_model')
    



def pad_to_size(vec, size):
  zeros = [0] * (size - len(vec))
  vec.extend(zeros)
  return vec

def sample_predict(sample_pred_text, pad):
  embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
  encoded_sample_pred_text = embed(sample_pred_text)

  if pad:
    encoded_sample_pred_text = pad_to_size(encoded_sample_pred_text, 64)
  encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
  predictions = model.predict(tf.expand_dims(encoded_sample_pred_text, 0))

  return (predictions)
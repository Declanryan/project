from django.apps import AppConfig
from tensorflow import keras
import tensorflow_hub as hub
import tensorflow_datasets as tfds
import tensorflow as tf
class DocApiConfig(AppConfig):

  name = 'doc_api'
  model = keras.models.load_model('my_model')
  dataset, info = tfds.load('imdb_reviews/subwords8k', with_info=True, as_supervised=True)
  encoder = info.features['text'].encoder

  def pad_to_size(vec, size):
    zeros = [0] * (size - len(vec))
    vec.extend(zeros)
    return vec

  def sample_predict(sample_pred_text, pad):
    encoded_sample_pred_text =  DocApiConfig.encoder.encode(sample_pred_text)

    if pad:
      encoded_sample_pred_text =  DocApiConfig.pad_to_size(encoded_sample_pred_text, 64)
      encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
      predictions = DocApiConfig.model.predict(tf.expand_dims(encoded_sample_pred_text, 0))

    return (predictions)
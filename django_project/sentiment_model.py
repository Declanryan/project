# declare imports
import tensorflow_datasets as tfds
import tensorflow as tf
import matplotlib.pyplot as plt

# define plot function
def plot_graphs(history, metric):
  plt.plot(history.history[metric])
  plt.plot(history.history['val_'+metric], '')
  plt.xlabel("Epochs")
  plt.ylabel(metric)
  plt.legend([metric, 'val_'+metric])
  plt.show()

# load dataset from tensorflow datasets
dataset, info = tfds.load('imdb_reviews/subwords8k', with_info=True, as_supervised=True)
print("dataset size: {}".format(len(dataset)))

# split data into train and test
train_dataset, test_dataset = dataset['train'], dataset['test']
print("Training entries: {}, test entries: {}".format(len(train_dataset), len(test_dataset)))

# define the text encoder
encoder = info.features['text'].encoder

# print out the size of the vocab
print('Vocabulary size: {}'.format(encoder.vocab_size))

# set the buffer and batch size
BUFFER_SIZE = 10000
BATCH_SIZE = 64


train_dataset = train_dataset.shuffle(BUFFER_SIZE)

# padded_batch method to zero-pad the sequences to the length of the longest string in the batch:
train_dataset = train_dataset.padded_batch(BATCH_SIZE)
test_dataset = test_dataset.padded_batch(BATCH_SIZE)

model = tf.keras.Sequential([
	# embedding layer stores one vector per word.
    tf.keras.layers.Embedding(encoder.vocab_size, 64, mask_zero=True),# embedding layer stores one vector per word.
    # A bidirectional lstm rnn layer that will pass the input
    # forward and backward through the rnn layer to learn long range word dependencies.
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64)),# bidirectional lstm 64 node hidden dense layer
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)# output layer
])

# Compile the model
model.compile(loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
              optimizer=tf.keras.optimizers.Adam(1e-4),
              metrics=['accuracy'])

# insert the data into the model for training
history = model.fit(train_dataset, epochs=10,
                    validation_data=test_dataset, 
                    validation_steps=30)

test_loss, test_acc = model.evaluate(test_dataset)# evaluate using the test data

model.save("saved_models/sentiment_model")


print('Test Loss: {}'.format(test_loss))
print('Test Accuracy: {}'.format(test_acc))

def pad_to_size(vec, size):
  zeros = [0] * (size - len(vec))
  vec.extend(zeros)
  return vec

def sample_predict(sample_pred_text, pad):
  encoded_sample_pred_text = encoder.encode(sample_pred_text)

  if pad:
    encoded_sample_pred_text = pad_to_size(encoded_sample_pred_text, 64)
  encoded_sample_pred_text = tf.cast(encoded_sample_pred_text, tf.float32)
  predictions = model.predict(tf.expand_dims(encoded_sample_pred_text, 0))

  return (predictions)

# predict on a sample text without padding.

sample_pred_text = ('The movie was cool. The animation and the graphics '
                    'were out of this world. I would recommend this movie.')
predictions = sample_predict(sample_pred_text, pad=False)
print(predictions)

# predict on a sample text with padding

sample_pred_text = ('The movie was cool. The animation and the graphics '
                    'were out of this world. I would recommend this movie.')
predictions = sample_predict(sample_pred_text, pad=True)
print(predictions)

plot_graphs(history, 'accuracy')

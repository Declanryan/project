# Define imports.
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt

print("Version: ", tf.__version__)
print("Eager mode: ", tf.executing_eagerly())
print("Hub version: ", hub.__version__)
print("GPU is", "available" if tf.config.list_physical_devices('GPU') else "NOT AVAILABLE")

#Download dataset and split into train and test.
train_data, test_data = tfds.load(name="imdb_reviews", split=["train", "test"], 
                                  batch_size=-1, as_supervised=True)
# Split each set into exaples and labels.
train_examples, train_labels = tfds.as_numpy(train_data)
test_examples, test_labels = tfds.as_numpy(test_data)

# Create validation set
x_val = train_examples[:10000]
partial_x_train = train_examples[10000:]

y_val = train_labels[:10000]
partial_y_train = train_labels[10000:]


# Explore the data  Each example is a sentence representing the movie review and a corresponding label.
# The sentence is not preprocessed in any way. The label is an integer value of either 0 or 1, where 0 is a negative review, and 1 is a positive review.
# print size of training and test 
print("Training entries: {}, test entries: {}".format(len(train_examples), len(test_examples)))

#print first 10 examples and labels.
train_examples[:10]
train_labels[:10]
print(train_examples[:1])

# Create the model.
# I am representing the text by converting sentences into embeddings vectors. i will use a pre-trained text embedding as the first layer
# which will have two advantages:
# 1-i  don't have to worry about text preprocessing,
# 2-I benefit from transfer learning.
# For this example we will use a model from TensorFlow Hub called google/tf2-preview/gnews-swivel-20dim/1.
# This is a Token based text embedding trained on English Google News 130GB corpus.

#  First layer is  a Keras layer that uses the TensorFlow Hub model to embed the sentences
embed = hub.load("https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim/1")

hub_layer = hub.KerasLayer(embed, output_shape=[20], input_shape=[], 
                           dtype=tf.string, trainable=True)

# The full model
model = tf.keras.Sequential()
model.add(hub_layer)# Adds in the hub layer
model.add(tf.keras.layers.Dense(16, activation='relu'))# Add in a dense layer with 16 hidden units and a relu activation
model.add(tf.keras.layers.Dense(1))# A dense layer with a single output layer 

model.summary()


# configure the model to use an optimizer and a loss function:
model.compile(optimizer='adam',
              loss=tf.losses.BinaryCrossentropy(from_logits=True),
              metrics=[tf.metrics.BinaryAccuracy(threshold=0.0, name='accuracy')])


# Train the model

# Train the model for 40 epochs in batches of 512 samples.
# This is 40 iterations over all samples in the x_train and y_train.
# While training, monitor the model's loss and accuracy on the 10,000 samples from the validation set:

history = model.fit(partial_x_train,
                    partial_y_train,
                    epochs=2,
                    batch_size=512,
                    validation_data=(x_val, y_val),
                    verbose=1)

# save the model
x = "i like this cat is on the mat"
print("string", x)
# x = embed(x)
a = np.array(list(x))

print("***************************")
print(model(a, training=False))

answer = model.predict(
    a, batch_size=None, verbose=1, steps=None, callbacks=None, max_queue_size=10,
    workers=1, use_multiprocessing=False
)

print("the answer is ", answer)

# model.save('models')

# And let's see how the model performs. Two values will be returned.
# Loss (a number which represents our error, lower values are better), and accuracy.

# results = model.evaluate(test_data, test_labels)

# print(results)



import keras
from keras import metrics
from keras.optimizers import Adam, RMSprop
from keras.models import Sequential
from keras.layers import Dense, Activation
import pandas as pd
import numpy
import matplotlib.pyplot as plt


# Load dataset
dataframe = pd.read_csv("csv1.csv")
dataset = dataframe.values
# split into training and test sets
# print (numpy.shape(dataset)[0]); # 15,007,319
split_point = int(round((numpy.shape(dataset)[0])*0.8));
X_train = dataset[0:split_point,0:5]
Y_train = dataset[0:split_point,5]
#print (Y_train[0:50])
X_test = dataset[split_point:numpy.shape(dataset)[0],0:5]
Y_test = dataset[split_point:numpy.shape(dataset)[0],5]
# normalize data
X_train = (X_train - X_train.mean(0)) / X_train.std(0)
X_test = (X_test - X_test.mean(0)) / X_test.std(0)
#print (X[0:50,:])

# Create network model
model = Sequential()
model.add(Dense(6, input_dim=5, activation='relu'))
model.add(Dense(5, activation='relu'))
model.add(Dense(4, activation='relu'))
model.add(Dense(3, activation='relu'))
model.add(Dense(1))
model.compile(loss='mean_absolute_error', optimizer='rmsprop', metrics=['accuracy'])

# Train network
history = model.fit(X_train, Y_train, validation_split=0.24, epochs=5, batch_size=128)

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

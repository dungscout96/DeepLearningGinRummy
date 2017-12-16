import keras
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.models import model_from_json
import pandas as pd
import numpy
import matplotlib.pyplot as plt

# Load dataset
dataframe = pd.read_csv("csv2.csv")
dataset = dataframe.values
# split into training and test sets
# print (numpy.shape(dataset)[0]); # 15,007,319
split_point = int(round((numpy.shape(dataset)[0])*0.8));
X_train = dataset[0:split_point,0:6]
Y_train = dataset[0:split_point,6]
X_test = dataset[split_point:numpy.shape(dataset)[0],0:6]
Y_test = dataset[split_point:numpy.shape(dataset)[0],6]
# normalize data
X_train = (X_train - X_train.mean(0)) / X_train.std(0)
X_test = (X_test - X_test.mean(0)) / X_test.std(0)
#print (X[0:50,:])

# Create network model
model = Sequential()
model.add(Dense(6, input_dim=6, activation='relu'))
model.add(Dense(5, activation='relu'))
model.add(Dense(4, activation='relu'))
model.add(Dense(3, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# Train network
history = model.fit(X_train, Y_train, validation_split=0.24, epochs=10, batch_size=128, verbose=2)

# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()

# SAVE MODEL TO DISK
# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")

# LOAD SAVED MODEL
# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")

# evaluate loaded model on test data
loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
score = loaded_model.evaluate(X_train, Y_train, verbose=0)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))

# Test prediction
dataframe = pd.read_csv("pred_test1.csv")
dataset = dataframe.values
test_input = dataset[:, 0:6]
print(numpy.shape(test_input))
#test_input = numpy.reshape(test_input, [1, 6])
pred = loaded_model.predict(test_input)
numpy.savetxt("prediction.txt", pred, delimiter=',')
print(pred)
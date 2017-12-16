import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.models import model_from_json
from keras import optimizers
import keras
print(keras.__version__)
# LOAD SAVED MODEL
# load json and create model
json_file = open('project2ModelKeras2.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("project2ModelKeras2.h5")
print("Loaded model from disk")

# evaluate loaded model on test data
loaded_model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy'])

# Test prediction
dataframe = pd.read_csv("csvP_X_small.csv", header=None)
dataset = dataframe.values
X_test = dataset;
print(np.shape(X_test))
dataframe = pd.read_csv("csvP_Y_small.csv", header=None)
dataset = dataframe.values
Y_test = dataset[:,0:1]
print(np.shape(Y_test))

# reshape X_train to be [samples][depth][width][height]
# X_train = X_train.reshape(np.shape(Y_train)[0],4,91) # number of rows is number of rows of training set
X_test = X_test.reshape(np.shape(Y_test)[0],4,52) # number of rows is number of rows of training set
l = [] #
for i in range(0,np.shape(Y_test)[0]): # for each sample
    array = np.split(X_test[i], 4, axis=1) # split the array vertically
    array_stack = np.stack(array, axis=0) # stack the split arrays --> add depth dimension
    l.append(array_stack)
X_test = np.stack(tuple(l)) # stack all of the samples
print(np.shape(X_test))
pred = loaded_model.predict(X_test)
np.savetxt("prediction.txt", pred, delimiter=',')
print(pred)

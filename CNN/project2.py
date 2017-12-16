import numpy as np
import os
from keras.datasets import mnist
import matplotlib.pyplot as plt
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D, ZeroPadding2D
#from keras.layers.convolutional import Convolution2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
import pandas as pd
K.set_image_dim_ordering('th')
seed = 7
np.random.seed(seed)

# 11/26/2017: modify model to implement explicit features input. Change loss function and training function
def trainModel():
    # load data
    print()
    # filePathX = os.path.dirname(os.path.abspath(__file__)) + "\csvP_explicit_hand_X.csv"
    filePathX = os.path.dirname(os.path.abspath(__file__)) + "\csvP_X.csv"
    dataframe = pd.read_csv(filePathX, header=None)
    dataset = dataframe.values
    # X_train = dataset[:, 0:91]
    X_train = dataset[:, 0:52]
    print(np.shape(X_train))
    # filePathY = os.path.dirname(os.path.abspath(__file__)) + "\csvP_explicit_hand_Y.csv"
    filePathY = os.path.dirname(os.path.abspath(__file__)) + "\csvP_Y.csv"
    dataframe = pd.read_csv(filePathY, header=None)
    dataset = dataframe.values
    Y_train = dataset[:,0:1]
    print(np.shape(Y_train))

    # reshape X_train to be [samples][depth][width][height]
    # X_train = X_train.reshape(np.shape(Y_train)[0],4,91) # number of rows is number of rows of training set
    X_train = X_train.reshape(np.shape(Y_train)[0],4,52) # number of rows is number of rows of training set
    l = [] #
    for i in range(0,np.shape(Y_train)[0]): # for each sample
        # array = np.split(X_train[i], 7, axis=1) # split the array vertically
        array = np.split(X_train[i], 4, axis=1) # split the array vertically
        array_stack = np.stack(array, axis=0) # stack the split arrays --> add depth dimension
        l.append(array_stack)
    X_train = np.stack(tuple(l)) # stack all of the samples
    print(np.shape(X_train))

    # get validation data
    X_split = np.split(X_train, [int(round((np.shape(X_train)[0])*0.8))])
    X_train = X_split[0]
    X_val = X_split[1]
    Y_split = np.split(Y_train, [int(round((np.shape(Y_train)[0])*0.8))])
    Y_train = Y_split[0]
    Y_val = Y_split[1]


    # build the model
    model = baseline_model()
    # Fit the model
    history = model.fit(X_train, Y_train, validation_data=(X_val, Y_val), epochs=1, batch_size=128, verbose=2)
    #history = model.fit(X_train, Y_train, validation_data=(X_val, Y_val), epochs=1, batch_size=10, verbose=2)
    print(history.history.keys())

    # plot training history
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
    # Final evaluation of the model
    #scores = model.evaluate(X_test, Y_test, verbose=0)
    #print("Baseline error: %.2f%%" % (100-scores[1]*100))

    # Save model
    model_json = model.to_json()
    modelFilePath = os.path.dirname(os.path.abspath(__file__)) + "\project2ModelKerasTrash.json"
    with open(modelFilePath, "w") as json_file:
        json_file.write(model_json)
    weightFilePath = os.path.dirname(os.path.abspath(__file__)) + "\project2ModelKerasTrash.h5"
    model.save_weights(weightFilePath)

''' For Keras 2
'''
def baseline_model():
    # create model
    model = Sequential()
    model.add(ZeroPadding2D(padding=((6,7),(2,2)), input_shape=(4, 4, 13), data_format='channels_first'))
    print(model.output_shape)
    model.add(Conv2D(64, (5,5), strides=1, padding='same',activation='relu', name='conv1'))
    model.add(Conv2D(64, (5,5), strides=1, padding='same',activation='relu', name='conv2'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (5,5), strides=1, padding='same',activation='relu', name='conv3'))
    model.add(Conv2D(64, (5,5), strides=1, padding='same',activation='relu', name='conv4'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))
    model.add(Flatten())
    model.add(Dense(1))
    #model.add(Dense(num_classes, activation='softmax'))
    # Compile model
    model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['accuracy'])
    return model

# trainModel()
'''
For Keras 1
def baseline_model():
    # create model
    model = Sequential()
    model.add(Convolution2D(20, 4, 4, input_shape=(5, 4, 13), border_mode='same', activation='relu'))
    #model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Convolution2D(20, 4, 4, border_mode='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.2)) # If omit this one and flatten --> dimension error
    model.add(Flatten())
    model.add(Dense(100, activation='sigmoid'))
    model.add(Dense(1))
    #model.add(Dense(num_classes, activation='softmax'))
    # Compile model
    model.compile(loss='mean_absolute_error', optimizer='rmsprop', metrics=['accuracy'])
    return model
'''
'''
# get test data
dataframe = pd.read_csv("csv3_X_test.csv", header=None)
dataset = dataframe.values
X_test = dataset[:, 0:65]
print(np.shape(X_test))
dataframe = pd.read_csv("csv3_Y_test.csv", header=None)
dataset = dataframe.values
Y_test = dataset[:]
print(np.shape(Y_test))
X_test = X_test.reshape(np.shape(Y_test)[0],4,65) # number of rows is number of rows of ground-truth set
l = [] #
for i in range(0,np.shape(Y_test)[0]):
    array = np.split(X_test[i], 5, axis=1)
    array_stack = np.stack(array, axis=0)
    l.append(array_stack)
X_test = np.stack(tuple(l))#
print(np.shape(X_test))
'''
# normalize data
#X_train = (X_train - X_train.mean(0)) / X_train.std(0)
#X_test = (X_test - X_test.mean(0)) / X_test.std(0)

#X_train = X_train.reshape((X_train.shape[0],1, 1, 365)).astype('float32')
#X_test = X_test.reshape(X_test.shape[0],1, 1, 365).astype('float32')
#print(X_train)
#print(X_test)

# one hot encode outputs
#Y_train = np_utils.to_categorical(Y_train)
#Y_test = np_utils.to_categorical(Y_test)
#num_classes = Y_test.shape[1]

# define a convolutional layer
# 5x5 local receptive fields, stride = 1, 20 feature maps. Max-pooling layer 2x2

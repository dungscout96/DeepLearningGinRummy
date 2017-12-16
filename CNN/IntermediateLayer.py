from keras.models import model_from_json
from keras.models import Model
import pandas as pd
import numpy as np

img_width = 128
img_height = 128

# LOAD THE NEURAL NET!
# load json and create model
json_file = open('../CNN/project2ModelKerasTrash.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# load weights into new model
model.load_weights("../CNN/project2ModelKerasTrash.h5")
print("loaded model")

from keras.applications import vgg16
model = vgg16.VGG16(weights='imagenet', include_top=False)
print(model.input)
#load test dataj
dataframe = pd.read_csv("project2_test.csv", header=None)
dataset = dataframe.values
X_test = dataset;
print(np.shape(X_test))
X_test = X_test.reshape(1,4,52) # number of rows is number of rows of training set
l = [] #
array = np.split(X_test[0], 4, axis=1) # split the array vertically
array_stack = np.stack(array, axis=0) # stack the split arrays --> add depth dimension
l.append(array_stack)
X_test = np.stack(tuple(l)) # stack all of the samples
print(np.shape(X_test))


layer_dict = dict([(layer.name, layer) for layer in model.layers])
from keras import backend as K
layer_name = 'block5_conv1'
filter_index = 0

layer_output = layer_dict[layer_name].output
print(layer_output)
loss = K.mean(layer_output[:,:,:,filter_index])
print(loss)
grads = K.gradients(loss, X_test)[0]
print(grads)
grads /= (K.sqrt(K.mean(K.square(grads))) + 1e-5)
iterate = K.function([X_test, [loss,grads]])
input_img_data = np.random.random((1,3,img_width, img_height)) * 20 + 128.
step = 1.
for i in range(20):
    loss_value, grads_value = iterate([input_img_data])
    input_img_data += grads_value * step

from scipy.misc import imsave
def deprocess_image(x):
    # normalize tensor: center on 0., ensure std is 0.1
    x -= x.mean()
    x /= (x.std() + 1e-5)
    x *= 0.1

    # clip to [0, 1]
    x += 0.5
    x = np.clip(x, 0, 1)

    # convert to RGB array
    x *= 255
    if K.image_data_format() == 'channels_first':
        x = x.transpose((1, 2, 0))
    x = np.clip(x, 0, 255).astype('uint8')
    return x

img = input_img_data[0]
img = deprocess_image(img)
imsave("%s_filter_%d.png" % (layer_name,filter_index),img)
# intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer(layer_name).output)

# intermediate_output = intermediate_layer_model.predict(X_test)
# print(intermediate_output)

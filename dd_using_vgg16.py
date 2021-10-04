# -*- coding: utf-8 -*-
"""DD using VGG16.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Elg597sYw5uSq8rGiDeoDOkORsZrbLVy
"""

from google.colab import drive 
drive.mount('/content/gdrive')

import pandas as pd 
df=pd.read_csv('gdrive/My Drive/inp/driver_imgs_list.csv')
df.head(5)

by_drivers = df.groupby('subject')
unique_drivers = by_drivers.groups.keys()
print(unique_drivers)

import tensorflow as tf
tf.test.gpu_device_name()
!ln -sf /opt/bin/nvidia-smi /usr/bin/nvidia-smi
!pip install gputil
!pip install psutil
!pip install humanize
import psutil
import humanize
import os
import GPUtil as GPU
GPUs = GPU.getGPUs()
gpu = GPUs[0]
def printm():
 process = psutil.Process(os.getpid())
 print("Gen RAM Free: " + humanize.naturalsize( psutil.virtual_memory().available ), " | Proc size: " + humanize.naturalsize( process.memory_info().rss))

from keras.applications.vgg16 import VGG16
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization, GlobalAveragePooling2D
from keras.models import Sequential, Model
from keras.preprocessing.image import ImageDataGenerator

def vgg_std16_model(img_rows, img_cols, color_type=3):
    nb_classes = 10
   
    vgg16_model = VGG16(weights="imagenet", include_top=False)
    
    for layer in vgg16_model.layers:
        layer.trainable = False
        
    x = vgg16_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(nb_classes, activation = 'softmax')(x)

    model = Model(vgg16_model.input, predictions)
    
    return model

print("Loading network...")
img_rows = 64
img_cols = 64
color_type = 1
print("Loading network...")
model_vgg16 = vgg_std16_model(img_rows, img_cols)

model_vgg16.summary()

model_vgg16.compile(loss='categorical_crossentropy',
                         optimizer='rmsprop',
                         metrics=['accuracy'])

train_datagen = ImageDataGenerator(rescale = 1.0/255, 
                                   shear_range = 0.2, 
                                   zoom_range = 0.2, 
                                   horizontal_flip = True, 
                                   validation_split = 0.2)

test_datagen = ImageDataGenerator(rescale=1.0/ 255, validation_split = 0.2)

img_rows = 64
img_cols = 64
color_type = 1
batch_size = 40
nb_epoch = 10
training_generator = train_datagen.flow_from_directory('gdrive/My Drive/inp/imgs/train', 
                                                 target_size = (img_rows, img_cols), 
                                                 batch_size = batch_size,
                                                 shuffle=True,
                                                 class_mode='categorical', subset="training")

validation_generator = test_datagen.flow_from_directory('gdrive/My Drive/inp/imgs/train', 
                                                   target_size = (img_rows, img_cols), 
                                                   batch_size = batch_size,
                                                   shuffle=False,
                                                   class_mode='categorical', subset="validation")
nb_train_samples = 17943
nb_validation_samples = 4481

from keras.callbacks import ModelCheckpoint, EarlyStopping
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=2)

checkpoint = ModelCheckpoint('gdrive/My Drive/saved_models/vgg16_model.hdf5', monitor='val_acc', verbose=1, save_best_only=True, mode='max')
history_v4 = model_vgg16.fit_generator(training_generator,
                         steps_per_epoch = nb_train_samples // batch_size,
                         epochs = 10, 
                         callbacks=[es, checkpoint],
                         verbose = 1,
                         class_weight='auto',
                         validation_data = validation_generator,
                         validation_steps = nb_validation_samples // batch_size)

import h5py
model_vgg16.load_weights('gdrive/My Drive/saved_model/weights_best_vgg16.hdf5')

def plot_vgg16_test_class(model, test_files, image_number):
    img_brute = test_files[image_number]

    im = cv2.resize(cv2.cvtColor(img_brute, cv2.COLOR_BGR2RGB), (img_rows,img_cols)).astype(np.float32) / 255.0
    im = np.expand_dims(im, axis =0)

    img_display = cv2.resize(img_brute,(img_rows,img_cols))
    plt.imshow(img_display, cmap='gray')

    y_preds = model.predict(im, batch_size=batch_size, verbose=1)
    print(y_preds)
    y_prediction = np.argmax(y_preds)
    print('Y Prediction: {}'.format(y_prediction))
    print('Predicted as: {}'.format(activity_map.get('c{}'.format(y_prediction))))
    
    plt.show()

import numpy as np
from glob import glob
import os
import cv2
from tqdm import tqdm

NUMBER_CLASSES = 10
# Color type: 1 - grey, 3 - rgb

def get_cv2_image(path, img_rows, img_cols, color_type=3):
    # Loading as Grayscale image
    if color_type == 1:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    elif color_type == 3:
        img = cv2.imread(path, cv2.IMREAD_COLOR)
    # Reduce size
    img = cv2.resize(img, (img_rows, img_cols)) 
    return img

def load_test(size=12, img_rows=64, img_cols=64, color_type=3):
    path = os.path.join('/content/gdrive/My Drive/inp/imgs/ourtest', '*.jpg')
    print("Path: ", path)
    files = sorted(glob(path))
    print(files)
    X_test, X_test_id = [], []
    total = 0
    files_size = len(files)
    print(files_size)
    for file in tqdm(files):
        if total >= size or total >= files_size:
            break
        file_base = os.path.basename(file)
        img = get_cv2_image(file, img_rows, img_cols, color_type)
        X_test.append(img)
        X_test_id.append(file_base)
        total += 1
    return X_test, X_test_id

def read_and_normalize_sampled_test_data(size, img_rows, img_cols, color_type=3):
    test_data, test_ids = load_test(size, img_rows, img_cols, color_type)
    
    test_data = np.array(test_data, dtype=np.uint8)
    test_data = test_data.reshape(-1,img_rows,img_cols,color_type)
    
    return test_data, test_ids

nb_test_samples = 12
test_files, test_targets = read_and_normalize_sampled_test_data(nb_test_samples, img_rows, img_cols, color_type)
print('Test shape:', test_files.shape)
print(test_files.shape[0], 'Test samples')

activity_map = {'c0': 'Safe driving', 
                'c1': 'Texting with right hand', 
                'c2': 'Talking on the phone with right hand', 
                'c3': 'Texting with left hand', 
                'c4': 'Talking on the phone with left hand', 
                'c5': 'Using radio', 
                'c6': 'Drinking', 
                'c7': 'Looking behind', 
                'c8': 'Makeup', 
                'c9': 'Talking to passenger'}

import matplotlib.pyplot as plt
batch_size = 40
def plot_vgg16_test_class(model, test_files, image_number):
    img_brute = test_files[image_number]

    im = cv2.resize(cv2.cvtColor(img_brute, cv2.COLOR_BGR2RGB), (img_rows,img_cols)).astype(np.float32) / 255.0
    im = np.expand_dims(im, axis =0)

    img_display = cv2.resize(img_brute,(img_rows,img_cols))
    plt.imshow(img_display, cmap='gray')

    y_preds = model.predict(im, batch_size=batch_size, verbose=1)
    print(y_preds)
    y_prediction = np.argmax(y_preds)
    print('Y Prediction: {}'.format(y_prediction))
    print('Predicted as: {}'.format(activity_map.get('c{}'.format(y_prediction))))
    
    plt.show()

plot_vgg16_test_class(model_vgg16, test_files, 1)

plot_vgg16_test_class(model_vgg16, test_files, 0)

plot_vgg16_test_class(model_vgg16, test_files, 2)

plot_vgg16_test_class(model_vgg16, test_files, 3)

plot_vgg16_test_class(model_vgg16, test_files, 4)

plot_vgg16_test_class(model_vgg16, test_files, 4)

plot_vgg16_test_class(model_vgg16, test_files, 6)

plot_vgg16_test_class(model_vgg16, test_files, 7)

plot_vgg16_test_class(model_vgg16, test_files, 8)

plot_vgg16_test_class(model_vgg16, test_files, 10)

plot_vgg16_test_class(model_vgg16, test_files, 11)

plot_vgg16_test_class(model_vgg16, test_files, 9)

import tensorflow as tf
import h5py
model = tf.keras.models.load_model('gdrive/My Drive/saved_model/weights_best_vgg16.hdf5')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open("converted_model.tflite", "wb").write(tflite_model)


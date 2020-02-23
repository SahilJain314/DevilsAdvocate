import tensorflow as tf
import keras

#from keras.models import load_model
import numpy as np
import bert
import os
from bert import BertModelLayer
from bert import bert_tokenization

# Tensorflow gpu configuration
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 1.0
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)


#===============================================================================
#=============================== init model ====================================
#===============================================================================

max_len = 384

bert_layer = None

pTrain_dir = 'cased_L-12_H-768_A-12'

def bLayer():
    global bert_layer

    pTrain_dir = 'cased_L-12_H-768_A-12'

    bert_params = bert.params_from_pretrained_ckpt(pTrain_dir)

    bert_layer = bert.BertModelLayer.from_params(bert_params, name="bert")

    bert_layer.apply_adapter_freeze()

    bert_layer.trainable = True

bLayer()
def loadBertCheckpoint():
    pTrain_dir = pTrain_dir
    checkpointName = os.path.join(pTrain_dir, "bert_model.ckpt")

    bert.load_stock_weights(bert_layer, checkpointName)


def model():

    i = tf.keras.layers.Input(shape = (max_len,), name ='input', dtype = 'int32')
    bertLayer = bert_layer(i)
    flat = tf.keras.layers.GlobalAveragePooling1D()(bertLayer)
    drop1 = tf.keras.layers.Dropout(.2)(flat)
    dense1 = tf.keras.layers.Dense(128,activation='relu')(flat)
    #dense1 = tf.keras.layers.Dropout(.2)(dense1)
    #dense1 = tf.keras.layers.Dense(128,activation='relu')(dense1)
    #dense1 = tf.keras.layers.Dropout(.2)(dense1)

    #dense1_1 = tf.keras.layers.Dense(128,activation ='relu')(drop1)
    #dense2 = tf.keras.layers.Dense(2,activation='tanh')(dense1)

    output = tf.keras.layers.Dense(2, activation = 'softmax', dtype='float32')(flat)

    model = tf.keras.models.Model(inputs=i, outputs = output)

    return model

mod = model()

opt = tf.keras.optimizers.Adam(0.000001)

mod.compile(loss=tf.keras.losses.binary_crossentropy,
              optimizer= opt,
              metrics=['categorical_accuracy','mean_absolute_error'])

mod.load_weights('BiasModel.h5')

mod.summary()



#===============================================================================
#================================ functions ====================================
#===============================================================================

def getDeepBias(text):
    global mod
    print(text)

    text.replace('\n',' ')
    tokenizer = bert_tokenization.FullTokenizer(vocab_file='vocab.txt', do_lower_case=False)
    tokens = tokenizer.tokenize(text)

    token_segments = []

    index = 382

    tmp = ['[CLS]']+tokens[:382]+['[SEP]']
    tmp = np.array(tmp)
    tmp = tokenizer.convert_tokens_to_ids(tmp)

    while len(tmp)<384:
        tmp.append(0)

    tmp = np.array(tmp)
    #print(tmp)
    #print(tmp.shape)
    #print('predicted')

    token_segments.append(tmp)

    while(index<len(tokens)):
        index += 382

        temp = ['[CLS]']+tokens[index-382:index]+['[SEP]']
        temp = tokenizer.convert_tokens_to_ids(temp)

        if len(temp)>100:
            while len(temp)<384:
                temp.append(0)
            temp = np.array(temp)
            token_segments.append(temp)

    token_segments = np.array(token_segments)

    print(token_segments.shape)
    preds = []

    for t in token_segments:
        print(t)
        preds.append(mod.predict(t.reshape(1,384)))

    avg  = [0,0]
    for i in preds:
        avg += i
    avg /= len(preds)
    print("avg:"+str(avg))

    return avg[0]

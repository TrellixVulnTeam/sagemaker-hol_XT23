import argparse, os
import numpy as np

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, BatchNormalization, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.utils import multi_gpu_model

if __name__ == '__main__':
        
    parser = argparse.ArgumentParser()

    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--learning-rate', type=float, default=0.01)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--gpu-count', type=int, default=os.environ['SM_NUM_GPUS'])
    parser.add_argument('--model-dir', type=str, default=os.environ['SM_MODEL_DIR'])
    parser.add_argument('--training', type=str, default=os.environ['SM_CHANNEL_TRAINING'])
    parser.add_argument('--validation', type=str, default=os.environ['SM_CHANNEL_VALIDATION'])
    
    args, _ = parser.parse_known_args()
    
    epochs     = args.epochs
    lr         = args.learning_rate
    batch_size = args.batch_size
    gpu_count  = args.gpu_count
    model_dir  = args.model_dir
    training_dir   = args.training
    validation_dir = args.validation
    
    x_train = np.load(os.path.join(training_dir, 'x_train.npy'))
    y_train = np.load(os.path.join(training_dir, 'y_train.npy'))
    x_val  = np.load(os.path.join(validation_dir, 'x_val.npy'))
    y_val  = np.load(os.path.join(validation_dir, 'y_val.npy'))
    
    # input image dimensions
    img_rows, img_cols = 28, 28

    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_val.shape[0], 'test samples')
    
    # Normalize pixel values
    x_train  = x_train.astype('float32')
    x_val    = x_val.astype('float32')
    x_train /= 255
    x_val   /= 255
    
    # Convert class vectors to binary class matrices
    num_classes = 10
#     y_train = keras.utils.to_categorical(y_train, num_classes)
#     y_val   = keras.utils.to_categorical(y_val, num_classes)
    
#     model = Sequential()
    
#     # 1st convolution block
#     model.add(Conv2D(64, kernel_size=(3,3), padding='same', input_shape=input_shape))
#     model.add(BatchNormalization(axis=batch_norm_axis))
#     model.add(Activation('relu'))
#     model.add(MaxPooling2D(pool_size=(2,2), strides=2))
    
#     # 2nd convolution block
#     model.add(Conv2D(128, kernel_size=(3,3), padding='valid'))
#     model.add(BatchNormalization(axis=batch_norm_axis))
#     model.add(Activation('relu'))
#     model.add(MaxPooling2D(pool_size=(2,2), strides=2))

#     # Fully connected block
#     model.add(Flatten())
#     model.add(Dense(512))
#     model.add(Activation('relu'))
#     model.add(Dropout(0.3))

#     # Output layer
#     model.add(Dense(num_classes, activation='softmax'))

    model = tf.keras.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    
    print(model.summary())

    if gpu_count > 1:
        model = multi_gpu_model(model, gpus=gpu_count)
        
#     model.compile(loss=keras.losses.categorical_crossentropy,
#                   optimizer=SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True),
#                   metrics=['accuracy', 'mse'])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])
    
    model.fit(x_train, y_train, batch_size=batch_size,
                  validation_data=(x_val, y_val), 
                  epochs=epochs,
                  verbose=1)
    
    score = model.evaluate(x_val, y_val, verbose=0)
    print('Validation loss    :', score[0])
    print('Validation accuracy:', score[1])
    
    model.save(args.model_dir + '/1')
    
#     # save Keras model for Tensorflow Serving
#     sess = K.get_session()
#     tf.saved_model.simple_save(
#         sess,
#         os.path.join(model_dir, 'model/1'),
#         inputs={'inputs': model.input},
#         outputs={t.name: t for t in model.outputs})
    
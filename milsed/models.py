# CREATED: 7/21/17 21:20 by Justin Salamon <justin.salamon@nyu.edu>

'''
MILSED models.

All model construction functions must implement the same API:

Parameters
----------
pump : Pump
    The Pump used to generate the features/labels
alpha : float
    The alpha parameter for the softmaxpool layer

Returns
-------
model
    Keras model
model_inputs
    Name(s) of input layer(s)
model_outputs
    Name(s) of output(s)

'''

import keras as K
import milsed.layers

MODELS = {'crnn1d': construct_crnn1d,
          'cnn1d': construct_cnn1d}


def construct_crnn1d(pump, alpha):
    '''
    CRNN with 1D conv encoder and Bi-GRU.

    Parameters
    ----------
    pump
    alpha

    Returns
    -------

    '''
    model_inputs = ['mel/mag']

    # Build the input layer
    layers = pump.layers()

    x_mag = layers['mel/mag']

    # Apply batch normalization
    x_bn = K.layers.BatchNormalization()(x_mag)

    x_sq = milsed.layers.SqueezeLayer()(x_bn)

    # First convolutional filter: a single 3-frame filters
    conv1 = K.layers.Convolution1D(64, 3,
                                   padding='same',
                                   activation='relu',
                                   kernel_initializer='he_uniform')(x_sq)
                                   # data_format='channels_last')(x_sq)

    # First recurrent layer: a 128-dim bidirectional gru
    rnn1 = K.layers.Bidirectional(K.layers.GRU(128,
                                               return_sequences=True))(conv1)

    n_classes = pump.fields['static/tags'].shape[0]

    p0 = K.layers.Dense(n_classes, activation='sigmoid')

    p_dynamic = K.layers.TimeDistributed(p0, name='dynamic/tags')(rnn1)

    p_static = milsed.layers.SoftMaxPool(alpha=alpha,
                                         axis=1,
                                         name='static/tags')(p_dynamic)

    model = K.models.Model([x_mag],
                           [p_dynamic, p_static])

    model_outputs = ['dynamic/tags', 'static/tags']

    return model, model_inputs, model_outputs


def construct_cnn1d(pump, alpha):
    '''
    CNN with 1D conv encoder.

    Parameters
    ----------
    pump
    alpha

    Returns
    -------

    '''
    model_inputs = ['mel/mag']

    # Build the input layer
    layers = pump.layers()

    x_mag = layers['mel/mag']

    # Apply batch normalization
    x_bn = K.layers.BatchNormalization()(x_mag)

    x_sq = milsed.layers.SqueezeLayer()(x_bn)

    # First convolutional filter: a single 3-frame filters
    conv1 = K.layers.Convolution1D(64, 3,
                                   padding='same',
                                   activation='relu',
                                   kernel_initializer='he_uniform')(x_sq)
                                   # data_format='channels_last')(x_sq)

    n_classes = pump.fields['static/tags'].shape[0]

    p0 = K.layers.Dense(n_classes, activation='sigmoid')

    p_dynamic = K.layers.TimeDistributed(p0, name='dynamic/tags')(conv1)

    p_static = milsed.layers.SoftMaxPool(alpha=alpha,
                                         axis=1,
                                         name='static/tags')(p_dynamic)

    model = K.models.Model([x_mag],
                           [p_dynamic, p_static])

    model_outputs = ['dynamic/tags', 'static/tags']

    return model, model_inputs, model_outputs
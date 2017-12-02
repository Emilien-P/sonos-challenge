import sklearn
import sklearn.svm as svm
import sklearn.linear_model as lm
import numpy as np
from abc import ABC, abstractmethod, ABCMeta

from keras import Sequential
from keras import utils
from keras.layers import Dense, Activation, Conv2D, Flatten, Dropout, LSTM
from keras.callbacks import EarlyStopping


class SpeakerClassifier:
    '''
    Attributes:
        method : String = classifier method to implement
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, method="linSVM", feature_extraction=None):
        self.method = method
        self.feature_extraction = feature_extraction
        self.feature_coef_ = None
        self.model = None

    @abstractmethod
    def fit(self, x, y, sample_weight=None):
        '''
        Fit the training data x, y to the model.
        Perform feature extraction if specified at init by the user.
        :param x: Array-like of sample features, shape=[n_sample, n_feature]
        :param y: Array-like of sample labels, shape=[n_sample]
        :param sample_weight: Vector of the sample weights. Optional with default value equals to None
        :return: None
        '''

        x = np.asarray(x)
        if self.feature_extraction:
            if self.feature_extraction == "Lasso":
                thresh = 0.01
                # use Lasso regression to select useful features
                lasso_model = lm.Lasso(alpha=0.1, copy_X=True, positive=True)
                lasso_model.fit(x, y)
                self.feature_coef_ = lasso_model.coef_
        else:
            self.feature_coef_ = np.ones(x.shape[1])


    def predict(self, x):
        '''
        Predicts the test data labels.
        :param x:
        :return: a prediction of the test data labels
        '''

        return self.model.predict(x)


class MLClassifier(SpeakerClassifier):
    '''
    Classifier based on straight-forward ML implementations through scikit library
    '''

    def __init__(self, method="linSVM", feature_extraction=None):
        super(MLClassifier, self).__init__(method, feature_extraction)
        if method == "linSVM":
            self.model = svm.LinearSVC()
        else:
            raise ValueError("The method {} of classifier if not recognized as ML method".format(method))

    def fit(self, x, y, sample_weight=None):
        super(MLClassifier, self).fit(x, y, sample_weight)
        nb_samples = x.shape[0]
        x = x.reshape(nb_samples, -1)
        self.model.fit(x, y, sample_weight)

    def predict(self, x):
        x = [x.flatten()]
        return super().predict(x)

class NNClassifier(SpeakerClassifier):
    '''
    Classifier based on Neural Network implementation through Keras library
    '''

    def __init__(self, method="seqNN", feature_extraction=None):
        super(NNClassifier, self).__init__(method, feature_extraction)
        self.history = None
        if method in ["seqNN", "CNN", "LSTM"]:
            self.model = Sequential()
            self.compiled = False
        else:
            raise ValueError("The method {} of classifier if not recognized as NN method".format(method))

    def addAndCompile(self, input_dim, n_users=2):
        assert(n_users < 33)
        if self.method == "seqNN":
            input_dim = input_dim[0] * input_dim[1]
            self.model.add(Dense(64, input_dim=input_dim))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            self.model.add(Dense(64))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            #output layer
            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))


            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
        elif self.method == "CNN":
            self.model.add(Conv2D(32, (2, 2), input_shape=input_dim))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            self.model.add(Conv2D(16, (2, 2)))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            self.model.add(Flatten())
            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))

            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
        elif self.method == "CNN":
            self.model.add(Conv2D(32, (2, 2), input_shape=input_dim))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            self.model.add(Conv2D(16, (2, 2)))
            self.model.add(Activation('relu'))

            self.model.add(Dropout(0.25))

            self.model.add(Flatten())
            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))

            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
        elif self.method == "LSTM":
            input_dim = (input_dim[0], input_dim[1])
            #TODO: REGENERATE WITH OTHER IMPLEMENTATION
            '''self.model.add(LSTM(64, return_sequences=True, input_shape=input_dim))
            self.model.add(LSTM(64, return_sequences=True))
            self.model.add(LSTM(64, return_sequences=False))'''
            self.model.add(LSTM(128, return_sequences=False, input_shape=input_dim))
            self.model.add(Dropout(0.25))

            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))

            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

        self.compiled = True
        #utils.plot_model(self.model, to_file=("results/model_" + self.method +"_architecture.png"))

    def fit(self, x, y, sample_weight=None, num_class=None, val_split=0, val_data=None):
        assert self.compiled
        y = utils.to_categorical(y, num_classes=num_class)
        super(NNClassifier, self).fit(x, y, sample_weight)
        if self.method == "seqNN":
            nb_samples = x.shape[0]
            x = x.reshape(nb_samples, -1)
            if val_data:
                val_data = (val_data[0].reshape(val_data[0].shape[0], -1), val_data[1])
        elif self.method == "CNN":
            x = x[:, :, :, np.newaxis]
            if val_data:
                val_data = (val_data[0][:, :, :, np.newaxis], val_data[1])
        self.history = self.model.fit(x, y, sample_weight, validation_split=val_split, validation_data=val_data,
                                      epochs=20) # callbacks=[EarlyStopping(monitor='val_loss')]
        return self.history

    def predict(self, x):
        if self.method == "seqNN":
            n = x.shape[0] * x.shape[1]
            x = x.reshape((1, n))
        elif self.method == "CNN":
            x = x[np.newaxis, :, :, np.newaxis]
        elif self.method == "LSTM":
            x = x[np.newaxis, :, :]
        print(super().predict(x))
        idx = np.argmax(super().predict(x))
        return idx

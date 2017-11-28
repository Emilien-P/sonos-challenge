import sklearn
import sklearn.svm as svm
import sklearn.linear_model as lm
import numpy as np
from abc import ABC, abstractmethod, ABCMeta

from keras import Sequential
from keras import utils
from keras.layers import Dense, Activation, Conv2D, Flatten, Dropout

#TODO: If the number of sample is not sufficient, Bootstrap the data

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
        self.model.fit(np.apply_along_axis(lambda row: np.multiply(row, self.feature_coef_), arr=x, axis=1), y,
                       sample_weight)

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
        if method == "seqNN":
            self.model = Sequential()
            self.compiled = False
        elif method == "CNN":
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

            self.model.add(Dense(64))
            self.model.add(Activation('relu'))

            #output layer
            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))


            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
        elif self.method == "CNN":
            self.model.add(Conv2D(64, (2, 2), input_shape=input_dim))
            self.model.add(Activation('relu'))

            self.model.add(Conv2D(32, (2, 2)))
            self.model.add(Activation('relu'))

            self.model.add(Flatten())
            self.model.add(Dense(n_users))
            self.model.add(Activation('softmax'))

            self.model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

        self.compiled = True

    def fit(self, x, y, sample_weight=None, num_class=None):
        assert self.compiled
        y = utils.to_categorical(y, num_classes=num_class)
        super(NNClassifier, self).fit(x, y, sample_weight)
        self.history = self.model.fit(np.apply_along_axis(lambda row: np.multiply(row, self.feature_coef_), arr=x,
                                                          axis=1), y, sample_weight)

    def predict(self, x):
        if self.method == "seqNN":
            x = x.reshape((1, 600))
        idx = np.argmax(super().predict(x))
        return idx

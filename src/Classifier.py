import sklearn.svm as svm
import sklearn.linear_model as lm
import numpy as np

class SpeakerClassifier():
    '''
    Attributes:
        method : String = classifier method to implement
    '''

    def __init__(self, method="linSVM", feature_extraction=None):
        self.method = method
        self.feature_extraction = feature_extraction
        if method == "linSVM":
            self.model = svm.LinearSVC()
        else: raise ValueError("The method {} of classifier if not recognized".format(method))

    def fit(self, x, y, sample_weight=None):
        '''
        Fit the training data x, y to the model.
        Perform feature extraction if specified at init by the user.
        :param x: Array-like of sample features, shape=[n_sample, n_feature]
        :param y: Array-like of sample labels, shape=[n_sample]
        :param sample_weight: Vector of the sample weights. Optional with default value equals to None
        :return: None
        '''

        if self.feature_extraction:
            if self.feature_extraction == "Lasso":
                thresh = 0.01
                #use Lasso regression to select useful features
                x = np.asarray(x)
                lasso_model = lm.Lasso(alpha=10)
                lasso_model.fit(x, y)
                x = x[lasso_model.coef_ >= thresh]

        self.model.fit(x, y, sample_weight)

    def predict(self, x):
        '''
        Predicts the test data labels.
        :param x:
        :return: a prediction of the test data labels
        '''

        return self.model.predict(x)



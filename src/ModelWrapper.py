import src.Classifier as Cl
import src.speechrec as sprec
from sklearn.metrics import accuracy_score, hamming_loss
from keras import utils
import numpy as np
import mfcc as mf
import json

class ModelWrapper():
    '''
    Wrap over a Classifier Model and interpret strings arguments to use it
    '''

    nb_users = 0
    users_map = {}
    bootstrap = False
    train_labels = np.empty((1, 1))

    def __init__(self, method="linSVM", bootstrap="1", dirpath="users_data/", trunk="50", delta=False):
        self.delta = delta
        if method == "linSVM":
            self.model = Cl.MLClassifier()
        elif method == "seqNN":
            self.model = Cl.NNClassifier()
        elif method == "CNN":
            self.model = Cl.NNClassifier("CNN")
        elif method == "LSTM":
            self.model = Cl.NNClassifier("LSTM")
        else:
            raise ValueError("Method not recognized")

        if bootstrap == "1":
            self.bootstrap = True

        self.dirpath = dirpath
        if delta:
            self.number_feature = 25
        else:
            self.number_feature = 12
        self.train_data = np.empty((1, int(trunk), self.number_feature))
        self.test_data = np.empty((1, int(trunk), self.number_feature))
        self.test_labels = np.empty((1, 1))
        self.trunk = int(trunk)

    def calibrate(self, user_name, nb_calibrations="5", existing_samples=False, nb_tests="0",
                  noise_red=False, norm=False, downsample=0):
        '''
        Calibrate for a new user of the speaker recognition system
        :param user_name: The name of the user
        :param nb_calibrations: Number of calibration samples
        :param dirpath: path where to store the user data
        :param trunk: where to cut in the mel freq time domain
        :param noise_red: bool to trigger the noise reduction
        :param norm: Normalize th input samples
        :param existing_samples: bool to indicate whether the samples already exists
        :param nb_tests: number of samples to use for testing
        :param downsample: int factor to downsample the input
        :return: None
        '''

        # update the number of users we have
        self.nb_users += 1
        self.users_map.update({self.nb_users - 1 : user_name})

        nb_calibrations = int(nb_calibrations)
        nb_tests = int(nb_tests)
        trunk = self.trunk

        if existing_samples == "0":
            for i in range(nb_calibrations):
                sprec.get_one_sample(self.dirpath+user_name.lower()+"{:0>4}.wav".format(i + 1))

        if not self.bootstrap:
            # Drop after trunk in the time domain as well as the first mel coef
            user_calibration_data = [(mf.get_mfcc(self.dirpath + user_name.lower() + "{:0>4}.wav".format(i + 1),
                                      delta=self.delta,
                                      noisereduction=noise_red,
                                      normalizemean=norm,
                                      downsample=downsample)[:trunk, 1:])
                                      for i in range(nb_calibrations)]
            self.train_data = np.concatenate((self.train_data, np.asarray(user_calibration_data)), axis=0)
            self.train_labels = np.concatenate((self.train_labels, np.tile([self.nb_users - 1], (nb_calibrations, 1))))

        else:
            for i in range(nb_calibrations):
                mfcc = (mf.get_mfcc(self.dirpath + user_name.lower() + "{:0>4}.wav".format(i + 1),
                                    delta=self.delta, normalizemean=norm, downsample=downsample)[:, 1:])
                n_timedomain = mfcc.shape[0]
                print(mfcc.shape)
                nb_bootstrap = n_timedomain - self.trunk
                step = 25
                assert nb_bootstrap > 0
                cal_data = [mfcc[j: j + self.trunk] for j in np.arange(0, nb_bootstrap, step)]
                self.train_data = np.concatenate((self.train_data, np.asarray(cal_data)), axis=0)
                self.train_labels = np.concatenate(
                    (self.train_labels, np.tile([self.nb_users - 1], (np.arange(0, nb_bootstrap, step).shape[0], 1))))

                print(self.train_labels)

        if(nb_tests > 0):
            # Drop after trunk in the time domain as well as the first mel coef
            user_testing_data = [(mf.get_mfcc(self.dirpath + user_name.lower() + "{:0>4}.wav".format(i + 1),
                                              delta=self.delta,
                                              noisereduction=noise_red,
                                              normalizemean=norm)[:trunk, 1:])
                                 for i in range(nb_calibrations, nb_tests + nb_calibrations)]

            self.test_data = np.concatenate((self.test_data, np.asarray(user_testing_data)), axis=0)
            self.test_labels = np.concatenate((self.test_labels, np.tile([self.nb_users - 1], (nb_tests, 1))))


    def compile_model(self, val_split=0, val_data=False):
        '''
        Fit the training data to the wrapped model
        :return: None
        '''
        if isinstance(self.model, Cl.NNClassifier):
            self.model.addAndCompile((self.trunk, self.number_feature, 1), self.nb_users)
            #drop the first one which is a zero
            if val_data:
                his = self.model.fit(self.train_data[1:], self.train_labels[1:], sample_weight=None,
                                     num_class=self.nb_users,
                                     val_split=val_split,
                                     val_data=(self.test_data[1:],
                                     utils.to_categorical(self.test_labels[1:], num_classes=self.nb_users)))
            else:
                his = self.model.fit(self.train_data[1:], self.train_labels[1:], sample_weight=None,
                                     num_class=self.nb_users, val_split=val_split)
            return his
        else:
            if val_data:
                nb_tests = self.test_data.shape[0] - 1
                self.model.fit(self.train_data[1:], self.train_labels[1:], sample_weight=None)
                predictions = self.model.model.predict(self.test_data[1:].reshape(nb_tests, -1))
                return accuracy_score(self.test_labels[1:], predictions), hamming_loss(self.test_labels[1:], predictions)
            else: self.model.fit(self.train_data[1:], self.train_labels[1:], sample_weight=None)


    def sample_and_predict(self):
        '''
        Take a command from a user, send the data to Google and make a guess about the user identity
        :return: a json-formatted string of the prediction
        '''
        return self.predict_from_audio(*sprec.get_audio())

    def predict_from_file(self, file_name, norm=False):
        '''
        Take a fileName, try to open it and returns the prediction of the wrapped model
        :param file_name: Name of the file to recognize
        :return: a json-formatted string of the prediction
        '''

        pred_data = (mf.get_mfcc(self.dirpath+file_name, normalizemean=norm)[:self.trunk, 1:])
        prediction = self.model.predict(pred_data)
        prediction = self.users_map[int(prediction)]

        answ = {"user_prediction" : prediction}

        return json.dumps(answ)

    def predict_from_audio(self, audio, recognizer):
        audio, google_pred = sprec.recognize(audio, recognizer, return_audio=True)
        sprec.save_audio(audio, self.dirpath+"sample_to_recognize.wav")
        pred_data = mf.get_mfcc(self.dirpath+"sample_to_recognize.wav")[:self.trunk, 1:]

        prediction = self.model.predict(pred_data)
        if isinstance(self.model, Cl.NNClassifier):
            prediction = self.users_map[prediction]
        else:
            prediction = self.users_map[prediction[0]]
        answ = {"user_prediction" : prediction,
                "google_sentence_prediction" : google_pred}

        return prediction, google_pred

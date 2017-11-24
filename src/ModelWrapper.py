import src.Classifier as Cl
import src.speechrec as sprec
import numpy as np
import src.mfcc as mf
import json

class ModelWrapper():
    '''
    Wrap over a Classifier Model and interpret strings arguments to use it
    '''

    nb_users = 0
    users_map = {}
    bootstrap = False
    train_data = np.empty((1, 50 * 12))
    train_labels = np.empty((1, 1))

    def __init__(self, method="CNN", bootstrap="0", dirpath="users_data/", trunk="50"):
        if method == "linSVM":
            self.model = Cl.MLClassifier()
        elif method == "seqNN":
            self.model = Cl.NNClassifier()
        elif method == "CNN":
            self.model = Cl.NNClassifier("CNN")
        else:
            raise ValueError("Method not recognized")

        if bootstrap == "1":
            self.bootstrap = True

        self.dirpath = dirpath

        self.trunk = int(trunk)

    def calibrate(self, user_name, nb_calibrations="5", existing_samples=False):
        '''
        Calibrate for a new user of the speaker recognition system
        :param user_name: The name of the user
        :param nb_calibrations: Number of calibration samples
        :param dirpath: path where to store the user data
        :param trunk: where to cut in the mel freq time domain
        :return: None
        '''

        # update the number of users we have
        self.nb_users += 1
        self.users_map.update({self.nb_users : user_name})

        nb_calibrations = int(nb_calibrations)
        trunk = self.trunk

        if not existing_samples:
            for i in range(nb_calibrations):
                sprec.get_one_sample(self.dirpath+user_name+"{:0>4}.wav".format(i))

        if not self.bootstrap:
            # Drop after trunk in the time domain as well as the first mel coef
            user_calibration_data = [(mf.get_mfcc(self.dirpath + user_name + "{:0>4}.wav".format(i))
                                      [:trunk, 1:]).flatten() for i in range(nb_calibrations)]

            self.train_data = np.concatenate((self.train_data, np.asarray(user_calibration_data)), axis=0)

            if isinstance(self.model, Cl.MLClassifier):
                self.train_labels = np.concatenate((self.train_labels, np.tile([self.nb_users], (nb_calibrations, 1))))
            elif isinstance(self.model, Cl.NNClassifier):
                # TODO: implement
                pass

        else:
            raise ValueError("Bootstrapping not implemented yet")

    def compile_model(self):
        '''
        Fit the training data to the wrapped model
        :return: None
        '''
        self.model.fit(self.train_data[1:], self.train_labels[1:], sample_weight=None)

    def sample_and_predict(self):
        '''
        Take a command from a user, send the data to Google and make a guess about the user identity
        :return: a json-formatted string of the prediction
        '''
        return self.predict_from_audio(*sprec.get_audio())

    def predict_from_file(self, file_name):
        '''
        Take a fileName, try to open it and returns the prediction of the wrapped model
        :param file_name: Name of the file to recognize
        :return: a json-formatted string of the prediction
        '''

        #TODO: prepare data for CNN if needed, modulize those predict methods
        pred_data = [(mf.get_mfcc(self.dirpath+file_name)[:self.trunk, 1:]).flatten()]
        prediction = self.model.predict(pred_data)
        prediction = self.users_map[int(prediction[0])]

        answ = {"user_prediction" : prediction}

        return json.dumps(answ)

    def predict_from_audio(self, audio, recognizer):
        audio, google_pred = sprec.recognize(audio, recognizer, return_audio=True)
        sprec.save_audio(audio, self.dirpath+"sample_to_recognize.wav")
        pred_data = mf.get_mfcc(self.dirpath+"sample_to_recognize.wav")[:self.trunk, 1:]

        prediction = self.model.predict(pred_data)
        prediction = self.users_map[prediction[0]]

        answ = {"user_prediction" : prediction,
                "google_sentence_prediction" : google_pred}

        return json.dumps(answ)

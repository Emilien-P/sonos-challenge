from sklearn.model_selection import StratifiedKFold
import numpy as np
from src import mfcc as mf
from sklearn.model_selection import cross_validate
from src.Classifier import MLClassifier, NNClassifier
import src.Classifier as Cl

class ValidationTester():
    '''
    This class serves as a wrapper for testing the Speaker recognition process.
    Attribute:
        speakerRecog : The Machine Learning Recognition Model you want to test
    '''

    def __init__(self, model):
        self.model = model

    def twoSpeakerRecognitionTest(self, k=3, dirpath="../resources/", n_samples=100):
        '''
        Perform cross-validation testing on the data
        :param k: number of splits
        :param dirpath: Path where the data is located
        :param n_samples: Number of samples / speaker to be considered
        :return: A dictionary of scores
        '''
        # Test data using cross-validation with parameter k
        trunk=50
        arr1 = [
            (mf.get_mfcc(dirpath+"cmu_us_awb_arctic/wav/arctic_a{:0>4}.wav".format(i + 1))[:trunk, 1:]).flatten()
            for i in range(n_samples)]
        arr2 = [
            (mf.get_mfcc(dirpath+"cmu_us_clb_arctic/wav/arctic_a{:0>4}.wav".format(i + 1))[:trunk, 1:]).flatten()
            for i in range(n_samples)]

        speaker1 = np.array(arr1, dtype=np.float64)
        speaker2 = np.array(arr2, dtype=np.float64)

        data = np.concatenate((speaker1, speaker2))
        labels = np.concatenate((np.repeat(0, n_samples), np.repeat(1, n_samples)))

        if isinstance(self.model, MLClassifier):
            scores = cross_validate(self.model.model, data, labels, cv=k, scoring='accuracy')
        elif isinstance(self.model, NNClassifier):

            if self.model.method == "CNN":
                print("reshape of input")
                data = np.apply_along_axis(lambda matrix: matrix.reshape(50, 12, 1), arr=data, axis=1)

            print(data.shape)

            his = self.model.model.fit(data, labels, epochs=10, verbose=1, shuffle=True, validation_split=1/k)
            scores = his.history["val_loss"]
        else:
            raise ValueError("The model is not recognized")

        return scores

    def basicTest(self, dirpath="../resources/", n_samples=5):
        trunk=50
        arr1 = [
            (mf.get_mfcc(dirpath+"cmu_us_awb_arctic/wav/arctic_a{:0>4}.wav".format(i + 1))[:trunk, 1:]).flatten()
            for i in range(n_samples)]
        arr2 = [
            (mf.get_mfcc(dirpath+"cmu_us_clb_arctic/wav/arctic_a{:0>4}.wav".format(i + 1))[:trunk, 1:]).flatten()
            for i in range(n_samples)]

        speaker1 = np.array(arr1, dtype=np.float64)
        speaker2 = np.array(arr2, dtype=np.float64)

        split = 200

        trainData = np.concatenate((speaker1[:split], speaker2[:split]))
        testData = np.concatenate((speaker1[split:], speaker2[split:]))
        trainlabels = np.concatenate((np.repeat(0, split), np.repeat(1, split)))
        testlabels = np.concatenate((np.repeat(0,n_samples - split), np.repeat(1, n_samples - split)))

        if isinstance(self.model, MLClassifier):
            self.model.fit(trainData, trainlabels)
            return self.model.predict(testData)
        elif isinstance(self.model, NNClassifier):
            #TODO : REDO THE LABELLING WHICH IS WRONG!!!!!!
            trainlabels = np.concatenate((np.tile([1, 0], (1, split)), np.tile([0, 1], (1, split))), axis=0).T
            testlabels = np.concatenate((np.tile([1, 0], (1, n_samples -split)), np.tile([0, 1], (1, n_samples - split))), axis=0).T
            if self.model.method == "CNN":
                print("reshape of input")
                trainData = np.apply_along_axis(lambda matrix: matrix.reshape(50, 12, 1), arr=trainData, axis=1)
                testData = np.apply_along_axis(lambda matrix: matrix.reshape(50, 12, 1), arr=testData, axis=1)

            his = self.model.model.fit(trainData, trainlabels, epochs=10, verbose=1)
            scores = self.model.model.predict(testData, verbose=1)
        else:
            raise ValueError("The model is not recognized")

        return scores


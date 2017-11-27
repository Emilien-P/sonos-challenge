from src import Classifier as Cl
from src import ValidationTester as Vt
from src import ModelWrapper as MW
from src import mfcc as mf
import numpy as np

if __name__ == '__main__':
    # Test data
    # Take 10 samples of our database / speaker

    wrapper = MW.ModelWrapper(method="CNN")

    wrapper.calibrate("emilien", existing_samples=True)

    wrapper.calibrate("ege", existing_samples=True)

    wrapper.compile_model()

    print(wrapper.predict_from_file("emilien0005.wav"))
    #see predict_from_audio to take a live sample

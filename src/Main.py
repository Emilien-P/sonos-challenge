from src import Classifier as Cl
from src import ValidationTester as Vt
from src import ModelWrapper as MW
import seaborn as sns
import matplotlib.pyplot as plt
from src import mfcc as mf
import numpy as np

if __name__ == '__main__':
    # Test data
    # Take 10 samples of our database / speaker

    wrapper = MW.ModelWrapper(method="CNN", bootstrap="1")

    wrapper.calibrate("emilien", existing_samples=True)

    wrapper.calibrate("ege", existing_samples=True)

    wrapper.calibrate("alvin", existing_samples=True)

    history = wrapper.compile_model()

    print(wrapper.predict_from_file("alvin0005.wav"))

    sns.set()
    plt.plot(history.history["loss"])
    plt.show()

    #see predict_from_audio to take a live sample

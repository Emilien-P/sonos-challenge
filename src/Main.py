from src import Classifier as Cl
from src import ValidationTester as Vt
from src import mfcc as mf
import numpy as np

if __name__ == '__main__':
    # Test data
    # Take 10 samples of our database / speaker

    model = Cl.MLClassifier()
    tester = Vt.ValidationTester(model)
    n_sample=50

    print(tester.basicTest(n_samples=n_sample))

    model = Cl.NNClassifier(method="seqNN")
    model.addAndCompile(50 * 12)
    tester = Vt.ValidationTester(model)
    print(tester.basicTest(n_samples=n_sample))


    model = Cl.NNClassifier(method="CNN")
    model.addAndCompile((50, 12, 1))
    tester = Vt.ValidationTester(model)
    print(tester.basicTest(n_samples=n_sample))
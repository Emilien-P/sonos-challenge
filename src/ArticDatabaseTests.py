import numpy as np
from src import mfcc as mf
from sklearn.model_selection import cross_validate
from src.Classifier import MLClassifier, NNClassifier
import src.ModelWrapper as MW
import seaborn as sns
import matplotlib.pyplot as plt

def accuracyTest(method, bootstrap, n_samples, n_tests=0):
    mw = MW.ModelWrapper(method, bootstrap, "../resources/")

    mw.calibrate("cmu_us_awb_arctic/wav/arctic_a", n_samples, n_tests, True)
    mw.calibrate("cmu_us_clb_arctic/wav/arctic_a", n_samples, n_tests, True)
    mw.calibrate("cmu_us_rms_arctic/wav/arctic_a", n_samples, n_tests, True)
    mw.calibrate("cmu_us_slt_arctic/wav/arctic_a", n_samples, n_tests, True)

    if method in ["CNN", "seqNN", "LSTM"]:
        hist = mw.compile_model(val_data=(n_tests != 0))
        if n_tests > 0:
            idx = np.argmax(hist.history["val_acc"])
            return hist.history["val_acc"][idx], hist.history["val_loss"][idx]
        else:
            return hist.history["acc"][-2], hist.history["loss"][-2]
    else:
        return mw.compile_model(val_data=(n_tests != 0))

def extensiveModelTesting():
    sns.set()
    plt.figure()
    method_set = ["seqNN", "CNN", "LSTM", "linSVM"]
    x = np.arange(1, 25, 1)
    y_acc = np.zeros(x.shape)
    y_loss = np.zeros(x.shape)

    fig, (ax_acc, ax_loss) = plt.subplots(nrows=2)

    for method in method_set:
        for idx, n_samples in enumerate(x):
            y_acc[idx], y_loss[idx] = accuracyTest(method, "1", n_samples, n_tests=50)

        ax_acc.plot(x, y_acc)
        if method != "linSVM":
            ax_loss.plot(x, y_loss)

    ax_loss.legend(method_set)
    ax_acc.legend(method_set)
    ax_acc.set_xlabel("number of samples")
    ax_acc.set_ylabel("maximal accuracy over 10 epochs")
    ax_loss.set_xlabel("number of samples")
    ax_loss.set_ylabel("loss")

    ax_loss.set_title("Loss of the models recognizing between two males and two females according to number of samples")
    ax_acc.set_title(
        "Accuracy of the models recognizing between two males and two females according to number of samples")

    fig.suptitle("Accuracy and loss over number of samples with samples extension")

    plt.show()

def accuracyWithLotOfSamplesModelTesting():
    sns.set()
    plt.figure()
    method_set = ["seqNN", "CNN", "LSTM", "linSVM"]
    x = np.arange(1, 500, 20)
    y_acc = np.zeros(x.shape)
    y_loss = np.zeros(x.shape)

    fig, (ax_acc, ax_loss) = plt.subplots(nrows=2)

    for method in method_set:
        for idx, n_samples in enumerate(x):
            y_acc[idx], y_loss[idx] = accuracyTest(method, "0", n_samples, n_tests=25)

        ax_acc.plot(x, y_acc)
        if method != "linSVM":
            ax_loss.plot(x, y_loss)

    ax_loss.legend(method_set)
    ax_acc.legend(method_set)
    ax_acc.set_xlabel("number of samples")
    ax_acc.set_ylabel("maximal accuracy over 10 epochs")
    ax_loss.set_xlabel("number of samples")
    ax_loss.set_ylabel("loss")

    ax_loss.set_title("Loss of the models recognizing between two males and two females according to number of samples")
    ax_acc.set_title(
        "Accuracy of the models recognizing between two males and two females according to number of samples")

    fig.suptitle("Accuracy and loss over number of samples without samples extension")

    plt.show()

def withVsWithoutBootstrap():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["linSVM", "seqNN", "CNN", "LSTM"]
    x = np.arange(6, 13, 1)
    y_with = np.zeros(x.shape)
    y_without = np.zeros(x.shape)

    for i, method in enumerate(method_set):
        for idx, n_samples in enumerate(x):
            y_with[idx], _ = accuracyTest(method, "1", n_samples, n_tests=50)

        p1 = plt.plot(x, y_with, c=clrs[i], label=method)

        for idx, n_samples in enumerate(x):
            y_without[idx], _ = accuracyTest(method, "0", n_samples, n_tests=50)
        p2 = plt.plot(x, y_without, linestyle='--', c=clrs[i])


    plt.legend()
    plt.xlabel("number of samples")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models with and without sample generation")

    plt.show()

def methodsAgainstNumberSpeakers():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["linSVM", "seqNN", "CNN", "LSTM"]
    x = np.arange(6, 13, 1)
    y_with = np.zeros(x.shape)
    y_without = np.zeros(x.shape)

    for i, method in enumerate(method_set):
        for idx, n_samples in enumerate(x):
            y_with[idx], _ = accuracyTest(method, "1", n_samples, n_tests=50)

        p1 = plt.plot(x, y_with, c=clrs[i], label=method)

        for idx, n_samples in enumerate(x):
            y_without[idx], _ = accuracyTest(method, "0", n_samples, n_tests=50)
        p2 = plt.plot(x, y_without, linestyle='--', c=clrs[i])


    plt.legend()
    plt.xlabel("number of samples")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models with and without sample generation")

    plt.show()



if __name__ == "__main__":
   extensiveModelTesting()
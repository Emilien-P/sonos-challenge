import numpy as np
from src import mfcc as mf
from sklearn.model_selection import cross_validate
from src.Classifier import MLClassifier, NNClassifier
import src.ModelWrapper as MW
import seaborn as sns
import matplotlib.pyplot as plt

def accuracyTest(method, bootstrap, n_samples, n_tests=0, nb_speakers=4, delta=False, norm=False, return_pair=False):
    mw = MW.ModelWrapper(method, bootstrap, "../resources/", delta=delta)

    speakers_id = ["awb", "clb", "rms", "slt", "bdl", "jmk", "ksp"]
    for idx in range(nb_speakers):
        id = speakers_id[idx]
        mw.calibrate("cmu_us_"+id+"_arctic/wav/arctic_a", n_samples, n_tests, True, norm=norm)

    if method in ["CNN", "seqNN", "LSTM"]:
        hist = mw.compile_model(val_data=(n_tests != 0))
        if n_tests > 0:
            idx = np.argmax(hist.history["val_acc"])
            return (hist.history["val_acc"][idx], hist.history["val_loss"][idx])
        else:
            return hist.history["acc"][-2], hist.history["loss"][-2]
    else:
        return mw.compile_model(val_data=(n_tests != 0))

def accuracyTestNoise(method, bootstrap, n_samples, n_tests=0, nb_speakers=4, delta=False, noise_red=False):
    mw = MW.ModelWrapper(method, bootstrap, "../resources/", delta=delta)
    mw.calibrate("cmu_us_" + "bdl" + "_sin/wav/arctic_a", n_samples, n_tests, True, noise_red=noise_red)
    mw.calibrate("cmu_us_" + "jmk" + "_arctic/wav/arctic_a", n_samples, n_tests, True, noise_red=noise_red)

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
            y_acc[idx], y_loss[idx] = accuracyTest(method, "0", n_samples, n_tests=50)

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

def withVsWithoutDelta():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["linSVM", "seqNN", "CNN", "LSTM"]
    x = np.arange(6, 13, 1)
    y_with = np.zeros((len(method_set), *x.shape))
    y_without = np.zeros((len(method_set), *x.shape))

    for i, method in enumerate(method_set):
        for idx, n_samples in enumerate(x):
            y_with[i, idx], _ = accuracyTest(method, "1", n_samples, n_tests=50, delta=True, nb_speakers=7)

        p1 = plt.plot(x, y_with[i], c=clrs[i], label=method)

        for idx, n_samples in enumerate(x):
            y_without[i, idx], _ = accuracyTest(method, "1", n_samples, n_tests=50, delta=False, nb_speakers=7)
        p2 = plt.plot(x, y_without[i], linestyle='--', c=clrs[i])


    np.savetxt("results/withDelta.txt", y_with)
    np.savetxt("results/withoutDelta.txt", y_without)
    plt.legend()
    plt.xlabel("number of samples")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models with and without delta MFCC features")

    plt.show()

def methodsAgainstNumberSpeakers():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["linSVM", "seqNN", "CNN", "LSTM"]
    x = np.arange(2, 8, 1)
    y_with = np.zeros((len(method_set), *x.shape))
    y_without = np.zeros((len(method_set), *x.shape))

    for i, method in enumerate(method_set):
        for idx, n_speakers in enumerate(x):
            y_with[i, idx], _ = accuracyTest(method, "1", n_samples=10, n_tests=50, nb_speakers=n_speakers)

        p1 = plt.plot(x, y_with[i], c=clrs[i], label=method)


    np.savetxt("results/methodsAgainstNumberSpeakers.txt", y_with)

    plt.legend()
    plt.xlabel("number of speakers")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models trained with 10 samples over the number of speakers")

    plt.show()

def methodsAgainstNumberSpeakersWithVariance():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["linSVM", "seqNN", "CNN", "LSTM"]
    x = np.arange(2, 8, 1)
    y_with_upper = np.zeros((len(method_set), *x.shape))
    y_with_middle = np.zeros((len(method_set), *x.shape))
    y_with_lower = np.zeros((len(method_set), *x.shape))

    for i, method in enumerate(method_set):
        for idx, n_speakers in enumerate(x):
            acc = np.sort([accuracyTest(method, "1", n_samples=10, n_tests=50, nb_speakers=n_speakers)[0],
                                 accuracyTest(method, "1", n_samples=10, n_tests=50, nb_speakers=n_speakers)[0],
                                 accuracyTest(method, "1", n_samples=10, n_tests=50, nb_speakers=n_speakers)[0]])
            y_with_lower[i, idx] = acc[0]
            y_with_middle[i, idx] = acc[1]
            y_with_upper[i, idx] = acc[2]

        p1 = plt.plot(x, y_with_middle[i], c=clrs[i], label=method)
        plt.fill_between(x, y_with_upper[i], y_with_lower[i], color=clrs[i], alpha=0.5)

    plt.legend()
    plt.xlabel("number of speakers")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models trained with 10 samples over the number of speakers")

    plt.show()

def withVsWithoutNoiseReduction():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["CNN", "LSTM"]
    x = np.arange(6, 11, 1)
    y_with = np.zeros((len(method_set), *x.shape))
    y_without = np.zeros((len(method_set), *x.shape))

    for i, method in enumerate(method_set):
        for idx, n_samples in enumerate(x):
            y_with[i, idx], _ = accuracyTestNoise(method, "1", n_samples, n_tests=10, delta=True, noise_red=True)

        p1 = plt.plot(x, y_with[i], c=clrs[i], label=method)

        for idx, n_samples in enumerate(x):
            y_without[i, idx], _ = accuracyTestNoise(method, "1", n_samples, n_tests=10, delta=True, noise_red=False)
        p2 = plt.plot(x, y_without[i], linestyle='--', c=clrs[i])


    np.savetxt("results/withNoiseReduction.txt", y_with)
    np.savetxt("results/withoutNoiseReduction.txt", y_without)
    plt.legend()
    plt.xlabel("number of samples")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models with and without noise reduction")

    plt.show()

def withVsWithoutNormalization():
    sns.set()
    plt.figure()
    clrs = sns.color_palette("husl", 5)
    method_set = ["CNN", "LSTM"]
    x = np.arange(6, 11, 1)
    y_with = np.zeros((len(method_set), *x.shape))
    y_without = np.zeros((len(method_set), *x.shape))

    for i, method in enumerate(method_set):
        for idx, n_samples in enumerate(x):
            y_with[i, idx], _ = accuracyTest(method, "1", n_samples, n_tests=50,norm=True)

        p1 = plt.plot(x, y_with[i], c=clrs[i], label=method)

        for idx, n_samples in enumerate(x):
            y_without[i, idx], _ = accuracyTest(method, "1", n_samples, n_tests=50, norm=False)
        p2 = plt.plot(x, y_without[i], linestyle='--', c=clrs[i])


    np.savetxt("results/withNorm.txt", y_with)
    np.savetxt("results/withoutNorm.txt", y_without)
    plt.legend()
    plt.xlabel("number of samples")
    plt.ylabel("maximal accuracy over 10 epochs")

    plt.title("Accuracy of the models with and without feature normalization")

    plt.show()



if __name__ == "__main__":
   extensiveModelTesting()
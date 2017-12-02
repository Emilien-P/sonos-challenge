import numpy as np
import src.ModelWrapper as MW
import seaborn as sns
import matplotlib.pyplot as plt

def addNoiseToAudio(audio, mean=0, std=1):
    length = audio.shape[0]
    noise = np.random.normal(mean, std, length)
    return noise + audio




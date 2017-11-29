#!/usr/bin/env python3

import wave, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import filtfilt
from scipy.io.wavfile import write

def usage():

    msg = "\n\tSpecify name of WAV audio file to be noise reduced.\n" + \
          "\n\tUsage: python speechrec.py filename.wav" + \
          "\n\texports a file output.wav"

    print(msg)

def reduce_noise(filename):

    """ Performs noise reduction on an input WAV file. Returns sample rate and output (numpy array)"""

    sampleRate, output_signal = firpm(filename, output="firpm_output.wav")

    return sampleRate, output_signal


def butterworth(input, output="butter_output.wav", plot=False):

    """ Apply a Butterworth (bandpass) filter to an input WAV file """

    (nChannels, sampWidth, sampleRate, nFrames, compType, compName) = input.getparams()

    # extract audio from wav file
    input_signal = input.readframes(-1)
    input_signal = np.fromstring(input_signal, 'Int16')
    print(input_signal)
    input.close()

    # Butterworth filter design
    N    = 5
    nyq  = 0.5 * sampleRate
    low_cutoff  = 300 / nyq
    high_cutoff = 5500 / nyq
    b, a = signal.butter(N, [low_cutoff, high_cutoff], btype='band')

    # apply filter
    output_signal = filtfilt(b, a, input_signal)

    if plot:
        # Plot input and output signals
        t = np.linspace(0, nFrames/sampWidth, nFrames, endpoint = False)
        plt.plot(t, input_signal, label='Input')
        plt.plot(t, output_signal, label='Output')
        plt.show()

    scaled = np.int16(output_signal/np.max(np.abs(output_signal)) * 32767)
    write(output, sampleRate, scaled)#np.int16(output_signal))

def wiener(input, output="wiener_output.wav", plot=False):

    """ Apply a Wiener filter to an input WAV file """

    (nChannels, sampWidth, sampleRate, nFrames, compType, compName) = input.getparams()

    # extract audio from wav file
    input_signal = input.readframes(-1)
    input_signal = np.fromstring(input_signal, 'Int16')
    print(input_signal)
    input.close()

    # Wiener filter design
    dim = 10
    output_signal = signal.wiener(input_signal, noise=80)


    if plot:
        # Plot input and output signals
        t = np.linspace(0, nFrames/sampWidth, nFrames, endpoint = False)
        plt.plot(t, input_signal, label='Input')
        plt.plot(t, output_signal, label='Output')
        plt.show()

    scaled = np.int16(output_signal/np.max(np.abs(output_signal)) * 32767)
    write(output, sampleRate, scaled)

def firpm(inputfile, output="firpm_output.wav", plot=False):

    """ Apply a FIRPM filter to an input WAV file """

    input = wave.open(inputfile,'r')

    (nChannels, sampWidth, sampleRate, nFrames, compType, compName) = input.getparams()

    # extract audio from wav file
    input_signal = input.readframes(-1)
    input_signal = np.fromstring(input_signal, 'Int16')
    print(input_signal)
    input.close()

    # Band-pass filter design parameters
    nyq         = sampleRate/2 # Nyquist sample rate, Hz
    band        = [300, 3000]  # Desired pass band, Hz; recommended [300, 3000]
    trans_width = 250          # Pass band transition, Hz; recommended 250
    numtaps     = 125          # Size of the FIR filter

    edges = [0, band[0] - trans_width,
             band[0], band[1],
             band[1] + trans_width, 0.5*nyq]
    firpm = signal.remez(numtaps, edges, [0, 1, 0], Hz=nyq, type="bandpass")
    output_signal = signal.lfilter(firpm, [1], input_signal)

    scaled = np.int16(output_signal/np.max(np.abs(output_signal)) * 32767)
    write(output, sampleRate, np.int16(output_signal))

    if plot:

        # Plot Frequency response
        w, h = signal.freqz(firpm)
        fig = plt.figure()
        plt.title('FIRPM Freq Response')
        plt.plot(w, 20*np.log10(abs(h)),'b')
        plt.show()


        # Plot input and output signals
        t = np.linspace(0, nFrames/sampWidth, nFrames, endpoint = False)
        plt.plot(t, input_signal, label='Input')
        plt.plot(t, output_signal, label='Output')
        plt.show()

    return sampleRate, output_signal

def noise_gate(input, output="noisegate_output.wav"):
    pass

if __name__=="__main__":

    if len(sys.argv) < 2:
        usage()
        quit()

    input = sys.argv[1]

    firpm(input, plot=True)
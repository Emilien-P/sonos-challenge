#!/usr/bin/env python3

import scipy.io.wavfile as wav
import numpy as np
import speechpy, sys

def usage():

	msg = "\n\tSpecify filename of audio file to get MFCC from.\n" + \
          "\n\tUsage: python mfcc.py filename.wav"

	print(msg)

def get_mfcc(filename):

	""" Returns the MFCC coefficients of a given WAV file as a numpy array """

	fs, signal = wav.read(filename)

	print('\nFile sampling frequency: ' + str(fs))

	mfcc = speechpy.mfcc(signal, 
		                 sampling_frequency = fs, 
		                 frame_length       = 0.020, 
		                 frame_stride       = 0.01,
		                 num_cepstral       = 13,
	                     num_filters        = 40, 
	                     fft_length         = 512, 
	                     low_frequency      = 0, 
	                     high_frequency     = None,
	                     dc_elimination     = True)

	mfcc_feature_cube = speechpy.extract_derivative_feature(mfcc)
	print(mfcc)
	print('mfcc feature cube shape: ', mfcc_feature_cube.shape)

	return mfcc

if __name__=="__main__":

	if len(sys.argv) < 2:
		usage()
		quit()

	filename = sys.argv[1]

	get_mfcc(filename)

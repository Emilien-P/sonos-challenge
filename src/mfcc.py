#!/usr/bin/env python3

import scipy.io.wavfile as wav
import numpy as np
import speechpy, sys

div = '='*70 + '\n'

def usage():

	msg = "\n\tSpecify filename of audio file to get MFCC from.\n" + \
          "\n\tUsage: python mfcc.py filename.wav"

	print(msg)

def get_mfcc(filename, verbose=False):
	def print_if(string, verb):
		if verb:
			print(string)

	""" Returns the MFCC of a given WAV file as a numpy array """

	print_if('\nMFCC (Mel Frequency Cepstral Coefficients)\n' + div, verbose)

	fs, signal = wav.read(filename)

	print_if('File sampling frequency: ' + str(fs) + '\n', verbose)

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
	if verbose:
            print('MFCC - dimension: ', mfcc_feature_cube.shape)
	print_if(mfcc, verbose)

	return mfcc

def get_mfe(filename):

	""" Returns the features and frame energies (both numpy arrays) of a given WAV file """

	print('\nMFE (filterbank energy features)\n' + div)

	fs, signal = wav.read(filename)

	print('File sampling frequency: ' + str(fs) + '\n')

	features, frame_energies = speechpy.mfe(signal, 
							                sampling_frequency = fs, 
							                frame_length       = 0.020, 
							                frame_stride       = 0.01,
						                    num_filters        = 40, 
						                    fft_length         = 512, 
						                    low_frequency      = 0, 
						                    high_frequency     = None)

	print('Features - dimension: ' + str(features.shape))
	print(features, '\n')

	print('Frame Energies - dimension: ' + str(frame_energies.shape))
	print(frame_energies)

	return features, frame_energies

if __name__=="__main__":

	if len(sys.argv) < 2:
		usage()
		quit()

	filename = sys.argv[1]

	get_mfcc(filename)
	get_mfe(filename)

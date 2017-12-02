#!/usr/bin/env python3

from __future__ import division
import numpy as np
import speechpy, sys
import scipy.io.wavfile as wav
from noisereduction import reduce_noise
import matplotlib.pyplot as plt
import audioop, wave

div = '='*70 + '\n'

def usage():

	msg = "\n\tSpecify filename of audio file to get MFCC from.\n" + \
          "\n\tUsage: python mfcc.py filename.wav"

	print(msg)

def resample(filename, factor, inchannels=1, outchannels=1):

	""" Resamples a WAV file to specified rate """

	inrate, signal = wav.read(filename)

	outrate = round(inrate/float(factor))

	print('\nDownsampling ' + str(inrate) + ' to ' + str(outrate))

	if inrate < outrate:
		print("Invalid inrate and outrate: "+ str(inrate) + ', ' + str(outrate))
		quit()

	s_read  = wave.open(filename, 'r')
	s_write = wave.open("resampled.wav", 'w')

	n_frames = s_read.getnframes()
	data     = s_read.readframes(n_frames)

	try:
		converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
		if outchannels == 1:
			converted = audioop.tomono(converted[0], 2, 1, 0)
	except:
		print('Failed to downsample wav')
		return False

	try:
		s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
		s_write.writeframes(converted)
	except:
		print('Failed to write wav')
		return False

	s_read.close()
	s_write.close()

	return True


def get_mfcc(filename, 
			 downsample     = 0,
	         delta          = False, 
             noisereduction = True, 
             normalizemean  = False, 
             numcoeff       = 13, 
             verbose        = False):
	def print_if(string, verb):
		if verb:
			print(string)

	""" Returns the MFCC of a given WAV file as a numpy array. Options include:
		delta:          append delta (velocity) features to MFCC; doubles # features per frame
		noisereduction: apply noise reduction before computing MFCC
		normalizemean:  output MFCC as normalized global mean - mutually exclusive from delta
		numcoeff:       specify number of cepstral coefficients; usually scaled linearly with sampling rate
		verbose:        enable detailed print statements

	"""
	# Perform downsampling and creates another downsampled wav file if specified
	if downsample > 0:
		print_if('Downsampling On by factor of ' + str(downsample), verbose)
		resample(filename, downsample)
		filename = "resampled.wav"
	else:
		print_if('Downsampling Off', verbose)

	# Perform noise reduction before calculating coefficients
	if noisereduction:
		print_if('Noise Reduction On', verbose)
		fs, signal = reduce_noise(filename)

	else:
		print_if('Noise Reduction Off', verbose)
		fs, signal = wav.read(filename)

	print_if('\nMFCC (Mel Frequency Cepstral Coefficients)\n' + div, verbose)

	print_if('File sampling frequency: ' + str(fs) + '\n', verbose)

	mfcc = speechpy.mfcc(signal, 
		                 sampling_frequency = fs, 
		                 frame_length       = 0.020, 
		                 frame_stride       = 0.020,    # Frame overlap amount (0.02 is no overlap)
		                 num_cepstral       = numcoeff, # Default 13; scale with sample rate
	                     num_filters        = 40, 
	                     fft_length         = 512, 
	                     low_frequency      = 0, 
	                     high_frequency     = None,
	                     dc_elimination     = True)

	mfcc_feature_cube        = speechpy.extract_derivative_feature(mfcc)
	length, numfeatures, dim = mfcc_feature_cube.shape

	print_if('MFCC dimension: ' + str(mfcc_feature_cube.shape), verbose) 
	print_if(mfcc, verbose)

	if delta:
		delta_features = get_delta(mfcc)
		mfcc_delta = np.empty((length, numfeatures*2))

		for i in range(len(mfcc)):
			mfcc_delta[i] = np.concatenate([mfcc[i], delta_features[i]])

		mfcc_delta_feature_cube = speechpy.extract_derivative_feature(mfcc_delta)
		print_if('\nMFCC with Delta dimension: ' + str(mfcc_delta_feature_cube.shape), verbose)
		print_if(mfcc_delta, verbose)

		return mfcc_delta

	# Option to return normalized cepstral mean (for each set of coeffs, subtracts mean from each coeff)
	if normalizemean:
		mfcc_normalizedmean = speechpy.cmvn(mfcc, variance_normalization=False)

		mfcc_normalizedmean_feature_cube = speechpy.extract_derivative_feature(mfcc_normalizedmean)
		print_if('\nMFCC with normalized mean dimension: ' + str(mfcc_normalizedmean_feature_cube.shape), verbose)
		print_if(mfcc_normalizedmean, verbose)

		return mfcc_normalizedmean

	return mfcc

def get_fft(filename, noisereduction=True):

	""" Returns FFT frequencies, power of input WAV file """

	# Perform noise reduction before calculating coefficients
	if noisereduction:
		print('Noise Reduction On')
		fs, signal = reduce_noise(filename)
	else:
		print('Noise Reduction Off')
		fs, signal = wav.read(filename)

	ps = np.abs(np.fft.fft(signal))**2
	print('FFT Power Spectrum')
	print(len(ps))
	print(ps)

	time_step = 1/fs
	freqs = np.fft.fftfreq(signal.size, time_step)
	print('Frequencies')
	print(freqs)
	print(len(freqs))
	#freqs = freqs[round(len(freqs)/2):]
	idx = np.argsort(freqs)

	plt.plot(freqs[idx], ps[idx])
	plt.show()

	return freqs[idx], ps[idx]

def get_delta(feat, N=1):

    """ Return delta features of given MFCC, N = # of deltas."""

    if N < 1:
        raise ValueError('N must be an integer >= 1')
    NUMFRAMES = len(feat)
    denominator = 2 * sum([i**2 for i in range(1, N+1)])
    delta_feat = np.empty_like(feat)
    padded = np.pad(feat, ((N, N), (0, 0)), mode='edge')
    for t in range(NUMFRAMES):
    	# [t : t+2*N+1] == [(N+t)-N : (N+t)+N+1]
        delta_feat[t] = np.dot(np.arange(-N, N+1), padded[t : t+2*N+1]) / denominator

    return delta_feat

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

	#downsample(filename)
	get_mfcc(filename, delta=True, verbose=True)
	# get_mfe(filename)
	# get_fft(filename)

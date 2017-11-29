#!/usr/bin/env python3

# Speech recognition and related audio utility functions
# Requires Python modules playsound, SpeechRecognition, pyaudio

import sys, playsound
import speech_recognition as sr  

def usage():

	msg = "\n\tSpecify name of WAV audio file to be saved.\n" + \
          "\n\tUsage: python speechrec.py filename.wav"

	print(msg)


def get_one_sample(file_name):
	audio, recognizer = get_audio()
	save_audio(audio, file_name)

def get_audio():

	""" Prompt the user to speak a phrase into the microphone """

	recognizer = sr.Recognizer()
	recognizer.pause_threshold = 0.5

	with sr.Microphone() as source:
	    recognizer.adjust_for_ambient_noise(source, duration = 1) 
	    playsound.playsound('ding.wav', True)
	    print('\nSay something!')
	    audio = recognizer.listen(source, 5)
	    print('Received audio, sending to Google...')

	return audio, recognizer

def recognize(audio, recognizer, return_audio=False):

	""" Use Google speech recognition to attempt to recognize given audio data """

	prediction = 'no prediction'

	try:
		prediction = recognizer.recognize_google(audio)
	except sr.UnknownValueError:
		print("Could not understand input")
	except sr.RequestError as e:
		print("Request Error; {0}".format(e))

	print("Prediction: " + prediction)

	if return_audio:
		return audio, prediction
	else:
		return prediction

def save_audio(audio, filename):

	""" Save recorded audio as a WAV file """

	with open(filename, "wb") as f:
		f.write(audio.get_wav_data())
	f.close()
	return

if __name__=="__main__":

	if len(sys.argv) < 2:
		usage()
		quit()

	filename = sys.argv[1]

	audio, recognizer = get_audio()
	prediction = recognize(audio, recognizer)
	save_audio(audio, filename)
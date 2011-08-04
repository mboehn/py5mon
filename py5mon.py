#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011 - Mathias Bøhn Grytemark
# Licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Thanks to Justin Peel at stackoverflow.com for some code (the important part
# which gets me the frequencies used). http://stackoverflow.com/questions/2648151/python-frequency-detection/2649540#2649540
#

###############
# Here are some defaults:

# lenght of file to inspect each run
frames = 1024
# play out loud?
play = False
# debug?
debug = False


###############
from optparse import OptionParser
import pyaudio
import wave
import numpy
import sys
import os

parser = OptionParser (usage="%prog [-d] [-p] FILE")
parser.add_option ("-d", "--debug", default=False, action='store_true', dest='debug', help='Enable debugging')
parser.add_option ("-p", "--play", default=False, action='store_true', dest='play', help='Play the file out loud')

(options, args) = parser.parse_args ()

# filename comes as a positional argument:
try:
	if args[0]:
		wavfile = args[0]
except:
	parser.print_help ()
	sys.exit(1)
if not os.path.isfile(wavfile):
	parser.print_help ()
	sys.exit(1)

if options.debug:
	debug = True
if options.play:
	play = True

if play:
	pa = pyaudio.PyAudio ()

wav = wave.open (wavfile, 'rb')
sw = wav.getsampwidth ()
rate = wav.getframerate ()
window = numpy.blackman (frames)


train = []
tonenone = 0
# need to remove decimals
def numdec (x):
	return int('{0:g}'.format(x))

# look for right frequencies...
def checkfreq (freq):
	if freq == 1124:
		tone = 1
	elif freq == 1197:
		tone = 2
	elif freq == 1275:
		tone = 3
	elif freq == 1358:
		tone = 4
	elif freq == 1446:
		tone = 5
	elif freq == 1540:
		tone = 6
	elif freq == 1640:
		tone = 7
	elif freq == 1747:
		tone = 8
	elif freq == 1860:
		tone = 9
	elif freq == 1981:
		tone = '0'
	elif freq == 2400:
		tone = 'a'
	elif freq == 930:
		tone = 'b'
	elif freq == 2247:
		tone = 'c'
	elif freq == 991:
		tone = 'd'
	elif freq == 2110:
		tone = 'e'
	elif freq == 1055:
		tone = 'f'
	else:
		return None
	return tone

# fix the train
def dotrain (train):
	lasttone = None
	newtrain = []

	for tone in train:
		if not tone == lasttone:
			newtrain.append (tone)
		lasttone = tone

	if not len (newtrain) == 5:
		return None
	
	lasttone = None
	for tone in newtrain:
		if tone == 'e' and lasttone:
			tone = lasttone
		sys.stdout.write(str(tone))
		lasttone = tone

	sys.stdout.write("\n")


# this is to actually play the file
if play:
	stream = pa.open (
		format = pa.get_format_from_width (sw),
		channels = wav.getnchannels (),
		rate = rate,
		output = True
		)

data = wav.readframes (frames)

while len (data) == frames*sw:
	if play:
		stream.write (data)
	
	indata = numpy.array (wave.struct.unpack ("%dh"%(len(data)/sw),data))*window
	fftData = abs (numpy.fft.rfft(indata))**2
	which = fftData[1:].argmax () + 1
	if which != len (fftData)-1:
		y0,y1,y2 = numpy.log (fftData[which-1:which+2])
		x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
		freq = (which + x1) * rate / frames
	else:
		freq = which * rate / frames
	freq = numdec(round (freq))

	tone = checkfreq (freq)
	if tone:
		if debug:
			print "Freq: %i (tone %s)" % (freq, tone)
		train.append (tone)
		tone = None	
	elif train and tone == None and tonenone == 3:
		dotrain (train)
		train = []
		tonenone = 0
	elif train and tone == None and tonenone == 0:
		tonenone = 1
	elif train and tone == None and tonenone == 1:
		tonenone = 2
	elif train and tone == None and tonenone == 2:
		tonenone = 3
	elif debug:
		print "Freq: %i" % (freq)

	data = wav.readframes (frames)

if data and play:
	stream.write (data)

if play:
	stream.close ()
	pa.terminate ()

if train:
	dotrain (train)

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
from optparse import OptionParser
import pyaudio
import wave
import numpy
import sys
import os

parser = OptionParser (usage="%prog [-d] [-i] [-p] FILE")
parser.add_option ("-d", "--debug", default=False, action='store_true', dest='debug', help='Enable debugging')
parser.add_option ("-p", "--play", default=False, action='store_true', dest='play', help='Play the file out loud')
parser.add_option ("-i", "--input", default=False, action='store_true', dest='input', help='Use line-in/mic as input instead of FILE. Do not specify FILE or -p with this.')
(options, args) = parser.parse_args ()

# lenght of file to inspect each run
frames = 1024


# play out loud?
if options.play:
	play = True
else:
	play = False

# debug?
if options.debug:
	debug = True
else:
	debug = False

# use mic/line-in?
if options.input:
	ainput = True
else:
	ainput = False


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

if play:
	pa = pyaudio.PyAudio ()

wav = wave.open (wavfile, 'rb')
sw = wav.getsampwidth ()
rate = wav.getframerate ()
window = numpy.blackman (frames)
train = []
tonenone = 0

reffreq = {}
reffreq['1'] = 1124
reffreq['2'] = 1197
reffreq['3'] = 1275
reffreq['4'] = 1358
reffreq['5'] = 1446
reffreq['6'] = 1540
reffreq['7'] = 1640
reffreq['8'] = 1747
reffreq['9'] = 1860
reffreq['0'] = 1981
reffreq['a'] = 2400
reffreq['b'] = 930
reffreq['c'] = 2247
reffreq['d'] = 991
reffreq['e'] = 2110
reffreq['f'] = 1055

# need to remove decimals
def numdec (x):
	return int('{0:g}'.format(x))

# look for right frequencies...
def checkfreq (freq, reffreq):
	for rtone, rfreq in reffreq.items():
		if rfreq-10 <= freq and rfreq+10 >= freq:
			return rtone


# clean the train
def cleantrain (train):
	lasttone = None
	newtrain = []

	for tone in train:
		if not tone == lasttone:
			newtrain.append (tone)
		lasttone = tone

	if len (newtrain) == 5:
		printtrain (newtrain)
	elif len (newtrain) == 10:
		atrain = newtrain[:5]
		btrain = newtrain[5:]
		printtrain (atrain)
		printtrain (btrain)
	elif len (newtrain) == 15:
		atrain = newtrain[:5]
		btrain = newtrain[:5]
		ctrain = newtrain[5:]
		printtrain (atrain)
		printtrain (btrain)
		printtrain (ctrain)

def printtrain (newtrain):
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
		output = True,
		output_device_index=None,
		)

if ainput:
	pass
else:
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

	tone = checkfreq (freq, reffreq)
	if tone:
		if debug:
			print "Freq: %i (tone %s)" % (freq, tone)
		train.append (tone)
		tone = None	
	elif train and tone == None and tonenone == 3:
		cleantrain (train)
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

	if ainput:
		pass
	else:
		data = wav.readframes (frames)

if data and play:
	stream.write (data)

if play:
	stream.close ()
	pa.terminate ()

if train:
	cleantrain (train)

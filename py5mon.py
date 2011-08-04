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

# lenght of file to inspect each run
frames = 1024

# play out loud?
play = True

# filename
wavfile = 'test.wav'

###############
import pyaudio
import wave
import numpy


pa = pyaudio.PyAudio ()
wav = wave.open (wavfile, 'rb')
sw = wav.getsampwidth ()
rate = wav.getframerate ()
window = numpy.blackman (frames)

# need to remove decimals
def numdec (x):
	return int('{0:g}'.format(x))


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
	print "Freq: %i" % (freq)
	data = wav.readframes (frames)

if data and play:
	stream.write (data)

if play:
	stream.close ()

pa.terminate ()



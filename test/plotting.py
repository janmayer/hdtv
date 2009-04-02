import numpy as np
import pylab as plt

from __main__ import *


def plot_pos(en, peak=1):
	plot(en, "pos", peak)

def plot_width(en, peak=1):
	plot(en, "fwhm", peak)


def plot_tr(en, peak=1):
	plot(en, "tr", peak)


def plot(en, param, peak):
	positions = list()
	errors = list()
	for ID in spectra.keys():
		spec = spectra[ID]
		try:
			fit = spec[en]
		except KeyError:
			pos = np.nan
			err = np.nan
		else:
			pos= getattr(fit.fitter.GetResults()[peak-1], param).value
			err = getattr(fit.fitter.GetResults()[peak-1], param).error
		positions.append(pos)
		errors.append(err)
	mean =average(positions, errors)
	print "Mean: %s" %mean
	fig = plt.figure()
	plt.axhline(y=mean)
	plt.errorbar(spectra.keys(), positions, errors, fmt='o')
	plt.show()


def average(values, errors):
	values = np.ma.masked_array(values, mask=np.isnan(values))
	errors = np.ma.masked_array(errors, mask=np.isnan(errors))
	weights = 1/errors**2
	return np.ma.average(values, weights=weights)
	
	

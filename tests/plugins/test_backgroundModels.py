"""
Test the different implemented background models with an artificial spectrum.
The test spectrum is a sequence of step functions with increasing step height. On each step, a normal-distributed peak is located. No artificial fluctuations have been introduced to give simple verifiable results.
The step on which the exponential background is tested has an exponentially decaying background on top of the step.
"""

import os

import pytest
import xml.etree.ElementTree as ET

from test.helpers.utils import hdtvcmd
from test.helpers.fixtures import temp_file

from numpy import arange, exp, ones, savetxt
from scipy.stats import norm

from hdtv.util import monkey_patch_ui
monkey_patch_ui()

import hdtv.cmdline
import hdtv.options
import hdtv.session

import __main__
try:
    __main__.spectra = hdtv.session.Session()
except RuntimeError:
    pass

from hdtv.plugins.specInterface import spec_interface
from hdtv.plugins.fitInterface import fit_interface
from hdtv.plugins.fitlist import fitxml

spectra = __main__.spectra

testspectrum = os.path.join(
    os.path.curdir, "test", "share", "test_spectrum_interpolation.tv")

# At the moment, the test spectrum has three steps with an 
# arbitrarily chosen length of 300 channels per step
NSTEPS = 3
NBINS_PER_STEP = 300
BG_PER_BIN = 10.
PEAK_WIDTH = 10.
PEAK_VOLUME = 100.

@pytest.fixture(autouse=True)
def prepare():
    """Create the test spectrum"""
    # Create an array for the bin centers
    bins = arange(NSTEPS*NBINS_PER_STEP)+0.5
    spectrum = ones(NSTEPS*NBINS_PER_STEP)
    # Create the three steps with increasing height
    for i in range(NSTEPS):
        spectrum[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP] = (i+1)*BG_PER_BIN*ones(NBINS_PER_STEP)
        # The peaks are located exactly in the centers of the steps
        spectrum = spectrum + PEAK_VOLUME*norm.pdf(bins, loc=i*NBINS_PER_STEP+0.5*NBINS_PER_STEP, scale=PEAK_WIDTH)
    
    # Add exponential background to the 3rd step
    spectrum[2*NBINS_PER_STEP:3*NBINS_PER_STEP] = spectrum[2*NBINS_PER_STEP:3*NBINS_PER_STEP] + BG_PER_BIN*exp((bins[2*NBINS_PER_STEP:3*NBINS_PER_STEP]-bins[2*NBINS_PER_STEP])/NBINS_PER_STEP)

    savetxt(testspectrum, spectrum) 

def test_backgroundRegions(temp_file):
    if not os.path.isfile(testspectrum):
        raise IOError('Test spectrum was not generated!')

    spec_interface.LoadSpectra(testspectrum)
    # Fit the first peak using an interpolated background
    f, ferr = hdtvcmd(
            'fit function background activate interpolation',
            'fit marker background set 50',
            'fit marker background set 100',
            'fit execute'
            )
    assert 'needs at least' in ferr

    f, ferr = hdtvcmd(
            'fit marker background set 200',
            'fit marker background set 225',
            'fit execute'
            )
    assert 'needs at least' in ferr

    f, ferr = hdtvcmd(
            'fit marker background set 225',
            'fit marker background set 250',
            'fit marker region set 120',
            'fit marker region set 180',
            'fit marker peak set 150',
            'fit execute',
            'fit store',
            'fit marker background delete 0',
            'fit marker background delete 1',
            'fit marker background delete 2',
            'fit marker region delete 0'
            )
    assert ferr == '' 

    # Fit the second peak using an polynomial background
    # with 'free' option for the number of background
    # parameters
    f, ferr = hdtvcmd(
            'fit function background activate polynomial',
            'fit parameter background free',
            'fit marker background set 350',
            'fit marker background set 400',
            'fit marker background set 500',
            'fit marker background set 525',
            'fit marker background set 525',
            'fit marker background set 550',
            'fit marker region set 420',
            'fit marker region set 480',
            'fit marker peak set 450',
            'fit execute',
            'fit store'
            )
    assert ferr == '' 

    # Fit the third peak using an exponential background
    # with 'free' option for the number of background
    # parameters
    f, ferr = hdtvcmd(
            'fit function background activate exponential',
            'fit parameter background 3',
            'fit marker background set 650',
            'fit marker background set 700',
            'fit marker background set 800',
            'fit marker background set 825',
            'fit marker background set 825',
            'fit marker background set 850',
            'fit marker region set 720',
            'fit marker region set 780',
            'fit marker peak set 750',
            'fit execute',
            'fit store'
            )
    assert ferr == '' 

    fitxml.WriteXML(spectra.Get("0").ID, temp_file)
    fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=True, interactive=False)

    # Read xml file manually and check correct output
    tree = ET.parse(temp_file)
    root = tree.getroot()
    fits = root.findall('fit')
    assert len(fits) == 3

    # Check the first fit (interpolation)
    # Check positions of background markers
    bgMarkers = fits[0].findall('bgMarker')
    assert len(bgMarkers) == 3
    assert float(bgMarkers[0].find('begin').find('cal').text) == 50.
    assert float(bgMarkers[0].find('end').find('cal').text) == 100.
    assert float(bgMarkers[1].find('begin').find('cal').text) == 200.
    assert float(bgMarkers[1].find('end').find('cal').text) == 225.
    assert float(bgMarkers[2].find('begin').find('cal').text) == 225.
    assert float(bgMarkers[2].find('end').find('cal').text) == 250.
    
    # Check background model and fit parameters 
    background = fits[0].find('background')
    assert background.get('backgroundModel') == 'interpolation'
    assert float(background.get('chisquare')) == 0.
    assert int(background.get('nparams')) == 6

    params = background.findall('param')
    assert float(params[0].find('value').text) == 75.
    assert abs(float(params[1].find('value').text) - 10.) < float(params[1].find('error').text)
    assert float(params[2].find('value').text) == 212.5
    assert abs(float(params[3].find('value').text) - 10.) < float(params[3].find('error').text)
    assert float(params[4].find('value').text) == 237.5
    assert abs(float(params[5].find('value').text) - 10.) < float(params[5].find('error').text)

    # Check peak and background areas 
    # The area of the peak should be PEAK_VOLUME
    # The area of the background should be BG_PER_BIN times the width of the fit region
    assert (abs(
            float(fits[0].find('peak').find('cal').find('vol').find('value').text) - PEAK_VOLUME) < 
            float(fits[0].find('peak').find('cal').find('vol').find('error').text
        )
    )

    integrals = fits[0].findall('integral')
    # Assert that the integrals are stored in the correct order.
    # Since the background integral has no uncertainty, the uncertainty
    # of the background integral is taken to be the uncertainty of the total 
    # integral.
    assert integrals[0].get('integraltype') == 'tot'
    assert integrals[1].get('integraltype') == 'bg'
    assert integrals[2].get('integraltype') == 'sub'
    assert len(integrals) == 3
    assert (abs(
        float(integrals[1].find('uncal').find('vol').find('value').text) - 60.*BG_PER_BIN) < 
        float(integrals[0].find('uncal').find('vol').find('error').text)
        )

    # Check the second fit (polynomial, free number of parameters)
    # Check positions of background markers
    bgMarkers = fits[1].findall('bgMarker')
    assert len(bgMarkers) == 3
    assert float(bgMarkers[0].find('begin').find('cal').text) == 350.
    assert float(bgMarkers[0].find('end').find('cal').text) == 400.
    assert float(bgMarkers[1].find('begin').find('cal').text) == 500.
    assert float(bgMarkers[1].find('end').find('cal').text) == 525.
    assert float(bgMarkers[2].find('begin').find('cal').text) == 525.
    assert float(bgMarkers[2].find('end').find('cal').text) == 550.

    # Check background model and fit parameters 
    background = fits[1].find('background')
    assert background.get('backgroundModel') == 'polynomial'
    # The following should be fulfilled for sure,
    # since we are fitting a constant background with 
    # a third-order polynomial
    assert float(background.get('chisquare')) < 1.
    assert int(background.get('nparams')) == 4

    params = background.findall('param')
    assert (
            abs(
                float(params[0].find('value').text) - 20.) < 
            float(params[0].find('error').text)
            )
    for i in range(1,4):
        assert abs(float(params[i].find('value').text)) < 0.1

    # Check peak and background areas 
    # The area of the peak should be PEAK_VOLUME
    # The area of the background should be BG_PER_BIN times the width of the fit region
    assert (abs(
            float(fits[1].find('peak').find('cal').find('vol').find('value').text) - PEAK_VOLUME) < 
            float(fits[1].find('peak').find('cal').find('vol').find('error').text
        )
    )

    integrals = fits[1].findall('integral')
    # Assert that the integrals are stored in the correct order.
    # Since the background integral has no uncertainty, the uncertainty
    # of the background integral is taken to be the uncertainty of the total 
    # integral.
    assert integrals[0].get('integraltype') == 'tot'
    assert integrals[1].get('integraltype') == 'bg'
    assert integrals[2].get('integraltype') == 'sub'
    assert len(integrals) == 3
    assert (abs(
        float(integrals[1].find('uncal').find('vol').find('value').text) - 2.*60.*BG_PER_BIN) < 
        float(integrals[0].find('uncal').find('vol').find('error').text)
        )

    # Check the third fit (exponential, fixed number of parameters)
    # The area of the peak should be PEAK_VOLUME
    # The area of the background should be BG_PER_BIN times the width of the fit region
    assert (abs(
            float(fits[2].find('peak').find('cal').find('vol').find('value').text) - PEAK_VOLUME) < 
            float(fits[2].find('peak').find('cal').find('vol').find('error').text
        )
    )


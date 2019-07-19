"""
Test the different implemented background models with an artificial spectrum.
The test spectrum is a sequence of step functions with increasing step height. On each step, a normal-distributed peak is located. No artificial fluctuations are introduced to give simple verifiable results.
Specific background models (for example the exponential background) may require particular shapes of the background, so their steps may be superimposed by another function.
"""

import os

import pytest
import xml.etree.ElementTree as ET

from test.helpers.utils import hdtvcmd, isclose
from test.helpers.fixtures import temp_file

from numpy import arange, exp, log, ones, savetxt, sqrt
from numpy.random import poisson
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
    os.path.curdir, "test", "share", "test_spectrum_background.tv")

# Set properties of the background spectrum
NSTEPS = 3
BG_REGIONS = [[0.1, 0.35], [0.65, 0.775], [0.775, 0.9]]
PEAK_WIDTH = 0.03
NBINS_PER_STEP = 300
BG_PER_BIN = 10.
PEAK_VOLUME = 500.
BG_TYPE = ['constant', 'exponential', 'constant']
POISSON_FLUCTUATIONS = [False, False, True, True]

BG_MARKER_TOLERANCE = 0.5
SIGMA_TO_FWHM = 2.3548299450 # = 2*sqrt(2*ln(2))
N_SIGMA = 2 # This number determines how many standard deviations (sigma) a fitted quantity
# may deviate from the ideal value. Sigma is either provided by some fitting algorithm or by 
# statistical considerations here.
# For the former case, this test is self-consistent and assumes that the algorithm estimates the
# uncertainty correctly.

@pytest.fixture(autouse=True)
def prepare():
    """Create the test spectrum"""
    # Create an array for the bin centers
    bins = arange(NSTEPS*NBINS_PER_STEP)+0.5
    spectrum = ones(NSTEPS*NBINS_PER_STEP)
    # Create the steps with increasing height
    for i in range(NSTEPS):
        if BG_TYPE[i] == 'constant':
            spectrum[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP] = BG_PER_BIN*ones(NBINS_PER_STEP)
        elif BG_TYPE[i] == 'exponential':
            spectrum[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP] = exp(log(BG_PER_BIN)+bins[i*NBINS_PER_STEP]/(0.5*NBINS_PER_STEP)-bins[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP]/(0.5*NBINS_PER_STEP))

        if POISSON_FLUCTUATIONS[i]:
            spectrum[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP] = poisson(spectrum[i*NBINS_PER_STEP:(i+1)*NBINS_PER_STEP])

        # The peaks are located exactly in the centers of the steps
        spectrum = spectrum + PEAK_VOLUME*norm.pdf(bins, loc=i*NBINS_PER_STEP+0.5*NBINS_PER_STEP, scale=PEAK_WIDTH*NBINS_PER_STEP)
    
    savetxt(testspectrum, spectrum) 

@pytest.mark.parametrize(
        "model, nparams, step, nregions, settings, errormessage, bgparams, bg_volume",
    [
        ("polynomial", 2, 0, 3, "fit parameter background 2", "", [10., 0.], 0.),
        ("polynomial", 3, 0, 3, "fit parameter background 3", "", [10., 0., 0.], 0.),
        ("interpolation", 6, 0, 2, "", "Background fit failed.", [], 0.),
        ("interpolation", 6, 0, 3, "", "", [
            0.5*(BG_REGIONS[0][0]+BG_REGIONS[0][1])*NBINS_PER_STEP, BG_PER_BIN,
            0.5*(BG_REGIONS[1][0]+BG_REGIONS[1][1])*NBINS_PER_STEP, BG_PER_BIN,
            0.5*(BG_REGIONS[2][0]+BG_REGIONS[2][1])*NBINS_PER_STEP, BG_PER_BIN
            ], 0.),
        ("exponential", 2, 1, 3, "fit parameter background 2", "", 
            [log(BG_PER_BIN)+2., -1./(0.5*NBINS_PER_STEP)], 
            0.5*NBINS_PER_STEP*exp(log(BG_PER_BIN)+2.)*(
                exp(-(1.5*NBINS_PER_STEP-3.*PEAK_WIDTH*NBINS_PER_STEP)/(0.5*NBINS_PER_STEP))-
                exp(-(1.5*NBINS_PER_STEP+3.*PEAK_WIDTH*NBINS_PER_STEP)/(0.5*NBINS_PER_STEP))
                )
            ),
    ]
    )
def test_backgroundRegions(model, nparams, step, nregions, settings, errormessage, bgparams, bg_volume, temp_file):
    if not os.path.isfile(testspectrum):
        raise IOError('Test spectrum was not generated!')

    spec_interface.LoadSpectra(testspectrum)
    command  = ['fit function background activate ' + model]
    if settings is not "":
        command.append(settings)
    for i in range(nregions):
        command.append('fit marker background set %f' % ((step+BG_REGIONS[i][0])*NBINS_PER_STEP))
        command.append('fit marker background set %f' % ((step+BG_REGIONS[i][1])*NBINS_PER_STEP))
    command.append('fit marker region set %f' % ((step+0.5)*NBINS_PER_STEP - 3.*PEAK_WIDTH*NBINS_PER_STEP))
    command.append('fit marker region set %f' % ((step+0.5)*NBINS_PER_STEP + 3.*PEAK_WIDTH*NBINS_PER_STEP))
    command.append('fit marker peak set %f' % ((step+0.5)*NBINS_PER_STEP))

    command.append('fit execute')
    command.append('fit store')
    for i in range(nregions):
        command.append('fit marker background delete %i' % (i))
    command.append('fit marker region delete 0')
    f, ferr = hdtvcmd(*command)

    batchfile = os.path.join(os.path.curdir, 'test', 'share', model + '_' + str(nparams) + '_' + str(step) + '_background.bat')
    bfile = open(batchfile, 'w')
    bfile.write('spectrum get '+ testspectrum + '\n')
    for c in command:
        bfile.write(c + '\n')
    bfile.close()

    if errormessage is not '':
        hdtvcmd('fit delete 0', 'spectrum delete 0')
        assert errormessage in ferr
    else:
        assert ferr == ''

        fitxml.WriteXML(spectra.Get("0").ID, temp_file)
        fitxml.ReadXML(spectra.Get("0").ID, temp_file, refit=True, interactive=False)
        hdtvcmd('fit delete 0', 'spectrum delete 0')

        # Parse xml file manually and check correct output
        tree = ET.parse(temp_file)
        root = tree.getroot()

        # Check the number of fits
        fits = root.findall('fit')
        assert len(fits) == 1

        # Check the number and positions of background markers
        bgMarkers = fits[0].findall('bgMarker')
        assert len(bgMarkers) == nregions
        for i in range(len(bgMarkers)):
            assert isclose(float(bgMarkers[i].find('begin').find('cal').text), (step+BG_REGIONS[i][0])*NBINS_PER_STEP, abs_tol=BG_MARKER_TOLERANCE)
            assert isclose(float(bgMarkers[i].find('end').find('cal').text), (step+BG_REGIONS[i][1])*NBINS_PER_STEP, abs_tol=BG_MARKER_TOLERANCE)
        # Check the number (and values) of background parameters
        background = fits[0].find('background')
        assert background.get('backgroundModel') == model
        assert int(background.get('nparams')) == nparams

        # Check the background parameters
        if len(bgparams) > 0:
            params = background.findall('param')
            for i in range(len(params)):
                assert isclose(float(params[i].find('value').text), bgparams[i], abs_tol=N_SIGMA*float(params[i].find('error').text))

        # Check the fit result
        # All results will be compared 
        assert isclose(float(fits[0].find('peak').find('cal').find('vol').find('value').text), PEAK_VOLUME, abs_tol=N_SIGMA*float(fits[0].find('peak').find('cal').find('vol').find('error').text)) 
        assert isclose(float(fits[0].find('peak').find('cal').find('width').find('value').text), SIGMA_TO_FWHM*PEAK_WIDTH*NBINS_PER_STEP, abs_tol=N_SIGMA*float(fits[0].find('peak').find('cal').find('width').find('error').text)) 

        # Check the integration result
        integrals = fits[0].findall('integral')
        assert len(integrals) == 3

        assert integrals[0].get('integraltype') == 'tot'
        assert integrals[1].get('integraltype') == 'bg'
        assert integrals[2].get('integraltype') == 'sub'
        # Peak volume
        assert isclose(float(integrals[2].find('uncal').find('vol').find('value').text), PEAK_VOLUME, abs_tol=N_SIGMA*float(integrals[2].find('uncal').find('vol').find('error').text))
        # Background volume
        if bg_volume > 0.:
            assert  isclose(float(integrals[1].find('uncal').find('vol').find('value').text), bg_volume, abs_tol=sqrt(bg_volume))
        else:
            assert isclose(float(integrals[1].find('uncal').find('vol').find('value').text), BG_PER_BIN*6.*PEAK_WIDTH*NBINS_PER_STEP, abs_tol=N_SIGMA*sqrt(BG_PER_BIN*6.*PEAK_WIDTH*NBINS_PER_STEP))

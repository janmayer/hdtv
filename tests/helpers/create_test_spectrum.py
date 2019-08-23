import os

from numpy import arange, exp, log, ones, savetxt, sqrt
from numpy.random import poisson
from scipy.stats import norm

# Set properties of the background spectrum
class ArtificialSpec:
    def __init__(self):
        self.nsteps = 3
        self.bg_regions = [[0.1, 0.35], [0.65, 0.775], [0.775, 0.9], [0.9, 0.95]]
        self.peak_width = 0.03
        self.nbins_per_step = 300
        self.bg_per_bin = 10.
        self.peak_volume = 500.
        self.bg_type = ['constant', 'exponential', 'constant']
        self.poisson_fluctuations = [False, False, True]
        self.spectrum = ones(self.nsteps*self.nbins_per_step)
        self.filename = os.path.join(
    os.path.curdir, "test", "share", "test_spectrum_background.tv")

    def create(self):
        """Create the test spectrum (if not already done)"""

        if not os.path.isfile(self.filename):
            # Create an array for the bin centers
            bins = arange(self.nsteps*self.nbins_per_step)+0.5
            spectrum = ones(self.nsteps*self.nbins_per_step)
            # Create the steps with increasing height
            for i in range(self.nsteps):
                if self.bg_type[i] == 'constant':
                    spectrum[i*self.nbins_per_step:(i+1)*self.nbins_per_step] = self.bg_per_bin*ones(self.nbins_per_step)
                elif self.bg_type[i] == 'exponential':
                    spectrum[i*self.nbins_per_step:(i+1)*self.nbins_per_step] = exp(log(self.bg_per_bin)+bins[i*self.nbins_per_step]/(0.5*self.nbins_per_step)-bins[i*self.nbins_per_step:(i+1)*self.nbins_per_step]/(0.5*self.nbins_per_step))

                if self.poisson_fluctuations[i]:
                    spectrum[i*self.nbins_per_step:(i+1)*self.nbins_per_step] = poisson(spectrum[i*self.nbins_per_step:(i+1)*self.nbins_per_step])

                # The peaks are located exactly in the centers of the steps
                spectrum = spectrum + self.peak_volume*norm.pdf(bins, loc=i*self.nbins_per_step+0.5*self.nbins_per_step, scale=self.peak_width*self.nbins_per_step)
            
            savetxt(self.filename, spectrum) 

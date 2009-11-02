import ROOT
import hdtv.weakref

from hdtv.spectrum import Histogram
from hdtv.drawable import Drawable, DrawableManager


class Histo2D():
    def __init__(self, hist2D):
        self.mhist = hist2D
        # FIXME
        self.xproj = None
        self.yproj = None
        
    def __str__(self):
        return self.name
        
    # name property
    def _get_name(self):
        if self.mhist:
            return self.mhist.GetTitle()
        
    def _set_name(self, name):
        self.hist.SetTitle(name)
        
    name = property(_get_name, _set_name)

    def Draw(self, viewport=None):
        viewer = ROOT.HDTV.Display.MTViewer(400, 400, self.mhist, self.name)
        self.matview = viewer


class MFHisto2D(Histo2D):
    """
    mfile-backed matrix
    """
    def __init__(self, fname, fmt=None, color=None, cal=None):
        self.fname = fname
#            
#        hdtv.dlmgr.LoadLibrary("mfile-root")
#        self.mhist = ROOT.MFileHist()

#        if not fmt or fmt.lower() == 'mfile':
#            result = self.mhist.Open(self.fname)
#        else:
#            result = self.mhist.Open(self.fname, fmt)
#            
#        if result != ROOT.MFileHist.ERR_SUCCESS:
#            raise SpecReaderError, mhist.GetErrorMsg()
#        Histo2D.__init__(self, ROOT.MFMatrix(self.mhist, 0))
        
#        # Load the projection (FIXME)
#        mhist_pry = ROOT.MFileHist()
#        result = mhist_pry.Open(self.fname.rsplit('.', 1)[0] + ".pry")
#        if result != ROOT.MFileHist.ERR_SUCCESS:
#            raise SpecReaderError, mhist_pry.GetErrorMsg()
#            
#        hist = mhist_pry.ToTH1D(self.fname + "_pry", self.fname + "_pry", 0, 0)
#        if not hist:
#            raise SpecReaderError, mhist_pry.GetErrorMsg()
        

#        
#    def __del__(self):
#        # Explicitly deconstruct C++ objects in the right order
#        self.vmat = None
#        ROOT.SetOwnership(self.mhist, True)
#        self.mhist = None

class CutSpectrum(Histogram):
    def __init__(self, hist, matrix, color=None, cal=None):
        Histogram.__init__(self, hist, color, cal)
        self.matrix = hdtv.weakref(matrix)
        self.typeStr = "cut spectrum (gated projection)"
        

class Matrix(DrawableManager):
    def __init__(self, histo2D, color, cal):
        DrawableManager.__init__(self)
        self.matrix = histo2D
        self.color = color
        self.cal = cal
    
    
        
        
        
        

import ROOT
import hdtv.color

from hdtv.weakref import weakref
from hdtv.spectrum import Spectrum
from hdtv.drawable import DrawableManager

######
# HACK for testing until low-level object is implemented
import copy
from hdtv.spectrum import FileHistogram  
class Histo2D(object):
    def __init__(self):
        self.projHisto = FileHistogram("test/mat/mat.prx")
        self.projHisto.typeStr = "Projection"
        self.cutHisto = FileHistogram("test/mat/cut.spc")
        self.cutHisto.typeStr = "Cut spectrum"
        
    @property
    def xproj(self):
        return copy.copy(self.projHisto)
        
    @property
    def yproj(self):
        return copy.copy(self.projHisto)
        
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return copy.copy(self.cutHisto)
#####
        
class CutSpectrum(Spectrum):
    def __init__(self,hist, matrix, axis):
        self.matrix = matrix
        self.axis = axis
        Spectrum.__init__(self, hist)
        
    def Show(self):
        """
        Show all visible cut markers for the axis of this spectrum
        """
        Spectrum.Show(self)
        if self.matrix:
            self.matrix.Show(axis=self.axis)

    def Hide(self):
        """
        Hide also the cut markers, but without chaning there visibility state in matrix 
        """
        Spectrum.Hide(self)
        if self.matrix:
            self.matrix.Hide()
        
    def Refresh(self):
        """
        Repeat the cut
        """
        if self.matrix:
            for cut in self.matrix.dict.itervalues():
                if self == cut.spec:
                    cut.Refresh()
                    break
        

class Matrix(DrawableManager):
    def __init__(self, histo2D, sym, viewport):
        DrawableManager.__init__(self, viewport)
        self.histo2D = histo2D
        self.sym = sym
        self.ID = None
        self._xproj=None
        self._yproj=None
        self._color = hdtv.color.default

#    # color property
    def _set_color(self, color):
        # give all cuts and projections the same color
        self._color = color
        for cut in self.dict.itervalues():
            cut.color = color
        if self._xproj is not None:
            self._xproj.color = color
        if self._yproj is not None:
            self._yproj.color = color
            
    def _get_color(self):
        return self._color
        
    color = property(_get_color, _set_color)
        
    # projections
    @property
    def xproj(self):
        return self.project(axis="x")
            
    @property
    def yproj(self):
        return self.project(axis="y")
        
    def project(self, axis):
        """
        Return Projection along a given axis
        """
        if getattr(self, "_%sproj" %axis) is None:
            # no valid link to that projection, create fresh object
            hist = getattr(self.histo2D, "%sproj" %axis)
            if self.sym:
                a = "0"
            else:
                a = axis
            proj = CutSpectrum(hist, self, axis=a)
            setattr(self, "_%sproj" %axis, weakref(proj))
            return proj
        else:
            return getattr(self, "_%sproj" %axis)
        
    def ExecuteCut(self, cut):
        if cut.axis == "x":
            axis = "y"
        elif cut.axis == "y":
            axis = "x"
        elif self.sym:
            axis = "0"
        else:
            raise RuntimeError
        cutHisto = self.histo2D.ExecuteCut(cut.regionMarkers, 
                                           cut.bgMarkers, axis)
        cutSpec = CutSpectrum(cutHisto, self, axis)
        cutSpec.color = self.color
        return cutSpec

    # overwrite some functions from Drawable
    def Insert(self, obj, ID=None):
        """
        Insert cut to internal dict
        """
        obj.color = self.color
        obj.dashed = True
        if ID is None:
            ID = self.activeID
        ID = DrawableManager.Insert(self, obj, ID)
        self.ActivateObject(ID)
        return ID


    def ActivateObject(self, ID):
        if ID is not None and ID not in self.ids:
            raise KeyError 
        # housekeeping for old active cut
        if self.activeID is not None:
            cut = self.GetActiveObject()
            cut.active = False
        # change active ID
        self.activeID = ID 
        self._iteratorID = self.activeID 
        # housekeeping for new active cut
        if self.activeID is not None:
            cut = self.GetActiveObject()
            cut.active = True

    def Show(self, axis="0"):
        for ID in self.visible:
            if self.dict[ID].axis==axis:
                self.dict[ID].Show()
    



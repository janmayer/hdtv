import ROOT
import hdtv.color

from hdtv.weakref import weakref
from hdtv.spectrum import Spectrum
from hdtv.drawable import DrawableManager

class Histo2D(object):
    def __init__(self):
        # HACK for testing until low-level object is implemented
        from hdtv.spectrum import FileHistogram  
        self.projHisto = FileHistogram("test/mat/mat.prx")
        self.projHisto.typeStr = "Projection"
        self.cutHisto = FileHistogram("test/mat/cut.spc")
        self.cutHisto.typeStr = "Cut spectrum"
        
    @property
    def xproj(self):
        return self.projHisto
        
    @property
    def yproj(self):
        return self.projHisto
        
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return self.cutHisto
        
        
class CutSpectrum(Spectrum):
    def __init__(self):
        self.cutRegionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            maxnum=1, color=hdtv.color.cut)
        self.cutBgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            color=hdtv.color.cut, connecttop=False)
        self.axis = None
        self.matrix = None
        Spectrum.__init__(self, histogram=None)
    
    # matrix property
    def _set_matrix(self, matrix):
        # cut spectrum only holds a weakref to matrix
        self._matrix = weakref(matrix)
        if self._matrix is None:
            self.hist = None
        
    def _get_matrix(self):
        return self._matrix
        
    matrix = property(_get_matrix, _set_matrix)
    
    # ID property
    def _get_ID(self):
        return self.cutRegionMarkers.ID
    
    def _set_ID(self, ID):
        self._ID = ID
        self.cutRegionMarkers.ID = ID

    ID = property(_get_ID, _set_ID)
    
    # cal property
    def _set_cal(self, cal):
        self._cal = hdtv.cal.MakeCalibration(cal)
        if self.viewport:
            self.viewport.LockUpdate()
        Spectrum.cal.fset(self, self._cal)
        self.cutRegionMarkers.cal = self._cal
        self.cutBgMarkers.cal = self._cal
        if self.viewport:
            self.viewport.UnlockUpdate()
    
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal,_set_cal)
    
    # color property
    def _set_color(self, color):
        if self.viewport:
            self.viewport.LockUpdate()
        Spectrum.color.fset(self, color)
        self.cutRegionMarkers.color = color
        self.cutBgMarkers.color = color
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)

    # active property
    def _set_active(self, state):
        if self.viewport:
            self.viewport.LockUpdate()
        Spectrum.active.fset(self, state)
        self.cutRegionMarkers.active = state
        self.cutBgMarkers.active = state
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_active(self):
        return self._active
        
    active = property(_get_active, _set_active)
        
    def Draw(self, viewport):
        self.viewport = viewport
        Spectrum.Draw(self, viewport)
        self.cutRegionMarkers.Draw(viewport)
        self.cutBgMarkers.Draw(viewport)
        
    def SetMarker(self, mtype, pos):
        if mtype is "":
            if self.cutRegionMarkers.IsFull():
                mtype="bg"
            else:
                mtype="region"
        markers = getattr(self, "cut%sMarkers" %mtype.title())
        markers.SetMarker(pos)
        
    def RemoveMarker(self, mtype, pos):
        markers = getattr(self, "cut%sMarkers" %mtype.title())
        markers.RemoveNearest(pos)
        
        
    def Cut(self, matrix, axis):
        self.matrix = matrix
        self.axis = axis
        self.hist = matrix.ExecuteCut(self.CutRegionMarkers, self.CutBgMarkers, axis)

class ProjSpectrum(Spectrum):
    def __init__(self, histo2D, axis):
        self.matrix = histo2D
        self.axis = axis
        hist = getattr(self.matrix.histo2D, "%sproj" %axis)
        Spectrum.__init__(self, hist)


class Matrix(DrawableManager):
    def __init__(self, histo2D):
        DrawableManager.__init__(self, viewport=None)
        self.histo2D = histo2D
        self._xproj=None
        self._yproj=None
    
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
            proj = ProjSpectrum(self, axis)
            setattr(self, "_%sproj" %axis, weakref(proj))
            return proj
        else:
            return getattr(self, "_%sproj" %axis)
        
#    def ExecuteCut(regionMarkers, bgMarkers, axis):
#        # FIXME: return hist and add a weakref to dict
#        pass

#    # overwrite some functions from Drawable
#    def Insert(obj, ID=None):
#        """
#        Insert cut (as weakref) to internal dict
#        """
#        pass

        
        

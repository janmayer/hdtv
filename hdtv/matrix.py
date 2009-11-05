import ROOT
import hdtv.weakref
import hdtv.color

from hdtv.spectrum import Spectrum
from hdtv.drawable import DrawableManager

class ProjSpectrum(Spectrum):
    def __init__(self, matrix, axis):
        hist = getattr(matrix.histo2D, "%sproj" %axis)
        Spectrum.__init__(self, hist)
        self.axis = axis
        self.matrix = matrix
    
    @property
    def ID(self):
        # FIXME: do some magic here
        return "%s.%s" %(self._ID, axis)


class CutSpectrum(Spectrum):
    def __init__(self):
        Spectrum.__init__(hist=None)
        self.cutRegionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            color=hdtv.color.cut)
        self.cutBgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            color=hdtv.color.cut, connecttop=False)
        self.axis = None
        self.matrix = None
    
    # matrix property
    def _set_matrix(self, matrix):
        # cut spectrum only holds a weakref to matrix
        self._matrix = hdtv.weakref(matrix)
        
    def _get_matrix(self):
        return self._matrix
        
    matrix = property(_get_matrix, _set_matrix)
    
    # ID property
    def _get_ID(self):
        return self.CutRegionMarkers.ID
    
    def _set_ID(self, ID):
        self._ID = ID
        self.CutRegionMarkers.ID = ID

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
        self.CutRegionMarkers.Draw(viewport)
        self.CutBgMarkers.Draw(viewport)
        
    def Cut(matrix, axis):
        self.matrix = matrix
        self.axis = axis
        self.hist = matrix.ExecuteCut(self.CutRegionMarkers, self.CutBgMarkers, axis)

class Matrix(DrawableManager):
    def __init__(self, histo2D):
        DrawableManager.__init__(self, viewport=None)
        self.histo2D = histo2D
    
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
            setattr(self, "_%sproj" %axis, hdtv.weakref(proj)
        return getattr(self, "_%sproj" %axis)
        
    def ExecuteCut(regionMarkers, bgMarkers, axis)
        # FIXME: return hist and add a weakref to dict
        pass

    # overwrite some functions from Drawable
    def Insert(obj, ID=None):
        """
        Insert cut (as weakref) to internal dict
        """
        # overwrite Drawable insert to use weakref instead of the real object
        obj = hdtv.weakref(obj)
        # FIXME: do some magic with IDs here, maybe by overwriting GetFreeID 
        Drawable.Insert(self, obj, ID)
        
        

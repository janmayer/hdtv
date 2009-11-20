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
        return self.projHisto
        
    @property
    def yproj(self):
        return self.projHisto
        
    def ExecuteCut(self, regionMarkers, bgMarkers, axis):
        return copy.copy(self.cutHisto)
#####
        
#class CutSpectrum(Spectrum):
#    def __init__(self):
#        self.cutRegionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
#                                            maxnum=1, color=hdtv.color.cut)
#        self.cutBgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
#                                            color=hdtv.color.cut, connecttop=False)
#        self.axis = None
#        self.matrix = None
#        Spectrum.__init__(self, histogram=None)
#    
#    # matrix property
#    def _set_matrix(self, matrix):
#        # cut spectrum only holds a weakref to matrix
#        self._matrix = weakref(matrix)
#        if self._matrix is None:
#            self.hist = None
#        
#    def _get_matrix(self):
#        return self._matrix
#        
#    matrix = property(_get_matrix, _set_matrix)
#    
#    # marker handling
#    def SetMarker(self, mtype, pos):
#        if mtype is "":
#            if self.cutRegionMarkers.IsFull():
#                mtype="bg"
#            else:
#                mtype="region"
#        markers = getattr(self, "cut%sMarkers" %mtype.title())
#        markers.SetMarker(pos)
#        
#    def RemoveMarker(self, mtype, pos):
#        markers = getattr(self, "cut%sMarkers" %mtype.title())
#        markers.RemoveNearest(pos)
#        

#    def ExecuteCut(self, matrix, axis):
#        """
#        get a valid hist for this cut markers
#        """
#        if not self.cutRegionMarkers.IsFull():
#            hdtv.ui.warn("Missing cut region marker")
#            return 
#        self.matrix = matrix
#        matrix.ExecuteCut(self)
#        
#    def __copy__(self):
#        """
#        copies marker of this cut
#        """
#        new = CutSpectrum()
#        for marker in self.cutRegionMarkers:
#            new.cutRegionMarkers.SetMarker(marker.p1.pos_cal)
#            if marker.p2:
#                new.cutRegionMarkers.SetMarker(marker.p2.pos_cal)
#        for marker in self.cutBgMarkers:
#            new.cutBgMarkers.SetMarker(marker.p1.pos_cal)
#            if marker.p2:
#                new.cutBgMarkers.SetMarker(marker.p2.pos_cal)
#        return new
#    
#    ### overwrite some stuff from the spectrum baseclass
#   
#    # color property
#    def _set_color(self, color):
#        if self.viewport:
#            self.viewport.LockUpdate()
#        Spectrum.color.fset(self, color)
#        self.cutRegionMarkers.color = color
#        self.cutBgMarkers.color = color
#        if self.viewport:
#            self.viewport.UnlockUpdate()
#            
#    def _get_color(self):
#        return Spectrum.color.fget(self)
#        
#    color = property(_get_color, _set_color)

#    # cal property
#    def _set_cal(self, cal):
#        if self.viewport:
#            self.viewport.LockUpdate()
#        Spectrum.cal.fset(self, cal)
#        self.cutRegionMarkers.cal = cal
#        self.cutBgMarkers.cal = cal
#        if self.viewport:
#            self.viewport.UnlockUpdate()
#    
#    def _get_cal(self):
#        return Spectrum.cal.fget(self)
#        
#    cal = property(_get_cal, _set_cal)
#    
#    def Draw(self, viewport):
#        self.viewport = viewport
#        Spectrum.Draw(self, viewport)
#        self.cutRegionMarkers.Draw(viewport)
#        self.cutBgMarkers.Draw(viewport)
#        
#    def Hide(self):
#        if self.viewport:
#            self.viewport.LockUpdate()
#        Spectrum.Hide(self)
#        self.cutRegionMarkers.Hide()
#        self.cutBgMarkers.Hide()
#        if self.viewport:
#            self.viewport.UnlockUpdate()
#            
#    def Show(self):
#        if self.viewport:
#            self.viewport.LockUpdate()
#        Spectrum.Show(self)
#        self.cutRegionMarkers.Show()
#        self.cutBgMarkers.Show()
#        if self.viewport:
#            self.viewport.UnlockUpdate()
#        
#    def Refresh(self):
#        self.ExecuteCut()
#        if self.viewport:
#            self.Draw(self.viewport)
    

class CutSpectrum(Spectrum):
    def __init__(self,hist, matrix, axis):
        self.matrix = matrix
        self.axis = axis
        Spectrum.__init__(self, hist)


class Matrix(DrawableManager):
    def __init__(self, histo2D, viewport):
        DrawableManager.__init__(self, viewport)
        self.histo2D = histo2D
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
            proj = CutSpectrum(hist, self, axis)
            setattr(self, "_%sproj" %axis, weakref(proj))
            return proj
        else:
            return getattr(self, "_%sproj" %axis)
        
    def ExecuteCut(self, cut):
        #FIXME: axis handling
        axis = cut.axis
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

#    
#    def Draw(self, viewport):
#        """
#        All objects of matrix are managed by other objects, 
#        there for the Draw function is blocked here.
#        """
#        pass # <-- this is on purpose!!!
        
        

import hdtv.color

from hdtv.weakref import weakref
from hdtv.drawable import Drawable

class Cut(Drawable):
    def __init__(self, color=None, cal=None):
        self.regionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            maxnum=1, color=hdtv.color.cut)
        self.bgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            color=hdtv.color.cut, connecttop=False)
        Drawable.__init__(self, color, cal)
        self.spec = None
        self.axis = None    #<- keep this last (needed for __setattr__)
        
    # delegate everthing to the markers
    def __setattr__(self, name, value):
        if name == "cal":
            value = hdtv.cal.MakeCalibration(value)
        if hasattr(self, "axis"):
            self.regionMarkers.__setattr__(name, value)
            self.bgMarkers.__setattr__(name, value)
        Drawable.__setattr__(self, name, value)
    
    # color property
    def _set_color(self, color):
        # we only need the passive color for fits
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.viewport:
            self.viewport.LockUpdate()
        self.regionMarkers.color = color
        self.bgMarkers.color = color
        if hasattr(self, "spec") and self.spec is not None:
            self.spec.color = color
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)

    def SetMarker(self, mtype, pos):
        if mtype is "":
            if self.regionMarkers.IsFull():
                mtype="bg"
            else:
                mtype="region"
        markers = getattr(self, "%sMarkers" %mtype)
        markers.SetMarker(pos)
        
    def RemoveMarker(self, mtype, pos):
        markers = getattr(self, "%sMarkers" %mtype)
        markers.RemoveNearest(pos)
    
    def ExecuteCut(self, matrix, axis):
        self.matrix = matrix
        self.axis = axis
        spec =  self.matrix.ExecuteCut(self)
        self.spec = weakref(spec)
        return spec
    
    def __copy__(self):
        """
        copies marker of this cut
        """
        new = Cut()
        for marker in self.regionMarkers:
            new.regionMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.regionMarkers.SetMarker(marker.p2.pos_cal)
        for marker in self.bgMarkers:
            new.bgMarkers.SetMarker(marker.p1.pos_cal)
            if marker.p2:
                new.bgMarkers.SetMarker(marker.p2.pos_cal)
        return new
    
    def Draw(self, viewport):
        if not viewport:
            return
        self.viewport = viewport
        self.regionMarkers.Draw(viewport)
        self.bgMarkers.Draw(viewport)
    
    def Hide(self):
        if not self.viewport:
            return
        self.viewport.LockUpdate()
        self.regionMarkers.Hide()
        self.bgMarkers.Hide()
        self.viewport.UnlockUpdate()
        
    def Show(self):
        if not self.viewport:
            return 
        self.viewport.LockUpdate()
        self.regionMarkers.Show()
        self.bgMarkers.Show()
        self.viewport.UnlockUpdate()
        
    def Refresh(self):
        if self.matrix:
            self.matrix.ExecuteCut(self, self.axis)
        
        
    

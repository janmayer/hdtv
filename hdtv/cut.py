import hdtv.color


class Cut(Drawable):
    def __init__(self, color=None, cal=None):
        self.regionMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            maxnum=1, color=hdtv.color.cut)
        self.bgMarkers = hdtv.marker.MarkerCollection("X", paired=True,
                                            color=hdtv.color.cut, connecttop=False)
        self.axis = None
        Drawable.__init__(self, color, cal)
        
    # color property
    def _set_color(self, color):
        # we only need the passive color for cuts
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.viewport:
            self.viewport.LockUpdate()
        self.regionMarkers.color = color
        self.bgMarkers.color = color
        if self.viewport:
            self.viewport.UnlockUpdate()
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)
    
    # cal property
    def _set_cal(self, cal):
        self._cal = hdtv.cal.MakeCalibration(cal)
        if self.viewport:
            self.viewport.LockUpdate()
        self.regionMarkers.cal = self._cal
        self.bgMarkers.cal = self._cal
        if self.viewport:
            self.viewport.UnlockUpdate()
    
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal,_set_cal)
    
    
    
    

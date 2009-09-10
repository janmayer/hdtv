# -*- coding: utf-8 -*-

# HDTV - A ROOT-based spectrum analysis software
#  Copyright (C) 2006-2009  The HDTV development team (see file AUTHORS)
#
# This file is part of HDTV.
#
# HDTV is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# HDTV is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with HDTV; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
import ROOT
import hdtv.cal
import hdtv.color
from hdtv.drawable import Drawable

from hdtv.util import Child, Position
import copy

class Marker(Drawable):
    """ 
    Markers in X or in Y direction
    
    Every marker contains a pair of positions as many markers come always in 
    pairs to mark a region (like background markers). Of course it is also 
    possible to have markers that consist of a single marker, then the second 
    possition is None.
    """
    def __init__(self, xytype, p1, color=hdtv.color.zoom, cal=None, connecttop=True, hasID=False):

        Child.__init__(self, parent=None)
        Drawable.__init__(self, parent=None, color=color, cal=cal)
        self.viewport = None
        self.displayObj = None
        self.xytype = xytype
        self.connecttop = connecttop
        self.p1 = p1
        self.p2 = None
        self.hasID = hasID
        # active color is set here and should not be changed afterwards
        self._activeColor = color
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        self.color = color
    
    # calibration
    def _set_cal(self, cal):
#        self._cal = hdtv.cal.MakeCalibration(cal)
        Drawable._set_cal(self, cal)
        self.Refresh()

    def _get_cal(self):
#        return self._cal
        return Drawable._get_cal(self)
 
    cal = property(_get_cal, _set_cal)
    
    # color
    def _set_color(self, color):
        # active color is given at creation and should not change
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        if self.displayObj:
            if self.active:
                self.displayObj.SetColor(self._activeColor)
            else:
                self.displayObj.SetColor(self._passiveColor)
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)


    def __str__(self):
        if not self.p2 is None:
            return '%s marker at %s and %s' %(self.xytype, self.p1, self.p2)
        else:
            return '%s marker at %s' %(self.xytype, self.p1)
    
    @property
    def title(self):
        title = str()
        
        if self.hasID:
            if self.parent is not None and self.parent.title is not None:
                title = self.parent.title
            
            title += str(self.parent.index(self)) 
        
        else:
            title = ""
            
        return title
    
    def Draw(self, viewport):
        """ 
        Draw the marker
        """
        if self.viewport:
            if self.viewport == viewport:
                # this marker has already been drawn
                # but maybe the position changed
                self.Refresh()
                return
            else:
                # Marker can only be drawn to a single viewport
                raise RuntimeError, "Marker cannot be realized on multiple viewports"
        self.viewport = viewport
        # adjust the position values for the creation of the makers
        # on the C++ side all values must be uncalibrated
        p1 = self.p1.GetPosInUncal()

        if self.p2 == None:
            n = 1
            p2 = 0.0
        else:
            n = 2
            p2 = self.p2.GetPosInUncal()
        # X or Y?
        if self.xytype == "X":
            constructor = ROOT.HDTV.Display.XMarker
        elif self.xytype == "Y":
            constructor = ROOT.HDTV.Display.YMarker
        if self.active:
            self.displayObj = constructor(n, p1, p2, self._activeColor)
        else:
            self.displayObj = constructor(n, p1, p2, self._passiveColor)
        if self.hasID:
            self.ShowTitle()
        if self.xytype=="X":
            # calibration makes only sense on the X axis
            self.displayObj.SetCal(self.cal)
            self.displayObj.SetConnectTop(self.connecttop)
        self.displayObj.Draw(self.viewport)
        

    def Refresh(self):
        """ 
        Update the position of the marker
        """
        ## TODO:
        ## Recalibration of markers should take place independently of an existing 
        ## viewport, so this check is commented out for now.
        ## Should be removed when it does not make problems elsewhere
        #if not self.viewport:
        #  return
        if self.displayObj:
            p1 = self.p1.GetPosInUncal()
            if not self.p2 is None:
                # on the C++ side all values must be uncalibrated
                p2 = self.p2.GetPosInUncal()
                self.displayObj.SetN(2)
                self.displayObj.SetPos(p1, p2)
            else:
                # on the C++ side all values must be uncalibrated
                self.displayObj.SetN(1)
                self.displayObj.SetPos(p1)
            if self.xytype == "X": # calibration makes only sense on the X axis
                self.displayObj.SetCal(self.cal)
            if self.active:
                self.displayObj.SetColor(self._activeColor)
            else:
                self.displayObj.SetColor(self._passiveColor)
            
            if self.hasID:
                self.ShowTitle()

    def Copy(self, cal=None):
        """
        Create a copy of this marker
        
        The actual position of the marker on the display (calibrated value)
        is kept. 
        """
        p1 = self.p1.GetPosInCal()
        new = Marker(self.xytype, p1, self.color, cal)
        # TODO:
        hdtv.ui.warn("TODO: Check Marker.Copy()")
        if self.p2 is not None:
            new.p2 = copy.copy(self.p2)
        return new


    def FixCal(self):
        self.p1.FixCal()
        if self.p2 is not None:
            self.p2.FixCal()
        
    def FixUncal(self):
        self.p1.FixUncal()
        if self.p2 is not None:
            self.p2.FixUncal()
            
    def ShowTitle(self):
        """
        Show the title of the marker (a string to be displayed aside it)
        """
        if self.displayObj:
            self.displayObj.SetTitle(self.title)


class MarkerCollection(list, Child):
    
    def __init__(self, xytype, paired=False, maxnum=None, color=None, cal=None, connecttop=True, hasIDs=False):
        list.__init__(self)
        Child.__init__(self, parent=None)
        self.viewport = None
        self.xytype = xytype
        self.paired = paired
        self.maxnum = maxnum
        self.connecttop = connecttop
        self.cal = cal
        self._activeColor = color
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        self.hasIDs = hasIDs
        self._fixedInCal = True # By default markers are fixed in calibrated space

    def __del(self):
        print "DEBUG MarkerColl destructor" 
        
    def __setitem__(self, m):
        m.parent = self
        list.__set_item__(self,m)
        
    def append(self, m):
        m.parent = self
        list.append(self,m)

    
    @property
    def title(self):
        if self.hasIDs:
            if not self.parent is None and not self.parent.title is None:
                title = self.parent.title + "."
            else:
                title = "."
        else:
            title = ""
        return title
        
    # color
    def _set_color(self, color):
        # active color is given at creation and should not change
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        for marker in self:
            marker.color = color
            
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)

    # calibration
    def _set_cal(self, cal):
        self._cal= hdtv.cal.MakeCalibration(cal)
        for marker in self:
            marker.cal = cal
            marker.Refresh()
            
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal,_set_cal)

    # active property
    @property
    def active(self):
        # an object is active, either when it is not belonging anywhere 
        if self.parent is None:
            return True
        # or when its parent is active
        if self.parent.active:
            try:
                # ask the parent for a decision
                return (self.parent.GetActiveObject() is self)
            except AttributeError:
                # otherwise all objects of that parent are active
                return True
        return False


    def Draw(self, viewport):
        self.viewport = viewport
        for marker in self:
            marker.Draw(self.viewport)
            

    def Show(self):
        for marker in self:
            marker.Show()
            

    def Hide(self):
        for marker in self:
            marker.Hide()
            

    def Remove(self):
        for marker in self[:]:
            marker.Remove()
            list.remove(self, marker)
        
    def Refresh(self):
        for marker in self:
            marker.Refresh()

    def FixCal(self):
        self._fixedInCal = True
        for marker in self:
            marker.FixCal()
    
    def FixUncal(self):
        self._fixedInCal = False
        for marker in self:
            marker.FixUncal()
            
            
    def PutMarker(self, pos):
        """
        Put a marker to calibrated position pos, possibly completing a marker pair
        """
 
        if not self.paired:
            m = Marker(self.xytype, pos, self._activeColor, self.cal, self.connecttop, hasID = self.hasIDs)
            m.color = self._passiveColor
            self.append(m)
            if self.viewport:
                m.Draw(self.viewport)
        else:
            if len(self)>0 and self[-1].p2==None:
                pending = self[-1]
                pending.p2 = pos
                pending.Refresh()
            elif self.maxnum and len(self)== self.maxnum:
                pending = self.pop(0)
                pending.p1 = pos
                pending.p2 = None
                pending.Refresh()
                self.append(pending)
            else:
                pending = Marker(self.xytype, pos, self._activeColor, self.cal,\
                                 self.connecttop, hasID = self.hasIDs)
                pending.color = self._passiveColor
                if self.viewport:
                    pending.Draw(self.viewport)
                self.append(pending)
                
    def IsFull(self):
        """
        Checks if this MarkerCollection already contains the maximum number of
        markers allowed
        """
        if self.maxnum == None:
            return False
        if len(self) > 0 and self[-1].p2 == None:
            return False
        return len(self) == self.maxnum
        
        
    def IsPending(self):
        """
        Checks if there is a single marker waiting to form a pair.
        Always returns False if this is a MarkerCollection with paired == False.
        """
        if not self.paired:
            return False
        return (len(self) > 0 and self[-1].p2 == None)
    
    
    def Clear(self):
        """
        Remove all markers from this collection
        """
        if self.viewport != None:
            self.viewport.LockUpdate()
        while self:
            self.pop().Remove()
        if self.viewport != None:
            self.viewport.UnlockUpdate()
        
        
    def RemoveNearest(self, pos):
        """
        Remove the marker that is nearest to pos
        If one of the members of a marker pair is nearest to pos, 
        both are removed
        """
        if len(self)==0:
            hdtv.ui.warn("No marker available, no action taken")
            return
        index = dict()
        for m in self:
            p1 = m.p1.GetPosInCal()
            diff = abs(pos-p1)
            index[diff] = m
            if self.paired and not m.p2==None:
                p2 = m.p2.GetPosInCal()

                diff = abs(pos-p2)
                index[diff] = m
        nearest = index[min(index.keys())]
        nearest.Remove()
        self.remove(nearest)
        self.Refresh()
        
    


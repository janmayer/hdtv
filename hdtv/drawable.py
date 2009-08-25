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
import os
import UserDict

import hdtv.cal
import hdtv.color
import hdtv.dlmgr
import hdtv.ui

hdtv.dlmgr.LoadLibrary("display")

class Drawable:
    def __init__(self, color=None, cal=None):
        self.viewport = None
        self.displayObj = None
        self.color = hdtv.color.Highlight(color, active=False)
        self.cal = hdtv.cal.MakeCalibration(cal)


    def __str__(self):
        return str(self.displayObj)


    def SetColor(self, color=None, active=False):
        """
        set color of the object 
        """
        if not color:
            # use old color
            color = self.color
        self.color = hdtv.color.Highlight(color, active)
        # update the display if needed    
        try:
            self.displayObj.SetColor(self.color)
        except:
            pass

    def SetCal(self, cal):
        """
        Set calibration

        The Parameter cal is either a sequence with the coefficients 
        of the calibration polynom:
        f(x) = cal[0] + cal[1]*x + cal[2]*x^2 + cal[3]*x^3 + ...
        or already a ROOT.HDTV.Calibration object
        """
        self.cal=hdtv.cal.MakeCalibration(cal)
        # update the display if needed
        try:
            self.displayObj.SetCal(self.cal)
        except:
            pass

    def Draw(self, viewport):
        """
        This function must create the appropriate object from the underlying
        C++ display code and call its draw function.
        Attention: Unlike the Display object of the underlying implementation,
        python objects can only be drawn on a single viewport
        """
        self.viewport = viewport

        
    def Refresh(self):
        """
        Refresh the objects data (e.g. reload a Spectrum from disk)
        """
        pass

    def Remove(self):
        """
        Remove the object 
        """
        if not self.viewport:
            return
        if self.displayObj:
            self.displayObj.Remove()
        self.displayObj = None
        # finally remove the viewport from this object
        self.viewport = None

    def Show(self):
        """
        Show the object 
        """
        if not self.viewport:
            return
        if self.displayObj:
            self.displayObj.Show()

    def Hide(self):
        """
        Hide the object 
        """
        if not self.viewport:
            return
        if self.displayObj:
            self.displayObj.Hide()

        
    def ToTop(self):
        """
        Move the spectrum to the top of its draw stack
        """
        if self.displayObj:
            try:
                self.displayObj.ToTop()
            except: # does not matter
                pass
            

    def ToBottom(self):
        """
        Move the spectrum to the top of its draw stack
        """
        if self.displayObj:
            try:
                self.displayObj.ToBottom()
            except: # does not matter
                pass


class DrawableCompound(UserDict.DictMixin):
    """
    This class is a prototype of a collection of drawable objects. 
    It provides some handy functions to manage such an collection.
    """
    def __init__(self, viewport):
        self.viewport = viewport
        self.objects = dict()
        self.visible = set()
        self.activeID = None
        self._iteratorID = self.activeID # This should keep track of ID for nextID, prevID
    
    # self.activeID getter and setter    
    def _set_activeID(self, ID):
        self.activeID = ID
        hdtv.ui.debug("hdtv.drawable._set_activeID: Resetting iterator to %d", self.activeID, level=6)
        self._iteratorID = self.activeID # Reset iterator
        
    def _get_activeID(self):
        return self.activeID
    
    activeID = property(_get_activeID, _set_activeID)
    
    # nextID/prevID getter
    @property
    def nextID(self):
        return self._nextID(onlyVisible = False)
    
    @property
    def nextVisibleID(self):
        return self._nextID(onlyVisible = True)

    @property
    def firstID(self):
        return self._firstID(onlyVisible = False)

    @property
    def firstVisibleID(self):
        return self._firstID(onlyVisible = True)

    @property
    def lastID(self):
        return self._lastID(onlyVisible = False)

    @property
    def lastVisibleID(self):
        return self._lastID(onlyVisible = True)

    def _firstID(self, onlyVisible = False):
        if onlyVisible:
            ids = list(self.visible)
        else:
            ids = self.keys()

        try:
            firstID = min(ids)
        except ValueError:
            firstID = self.activeID
        
        self._iteratorID = firstID
        hdtv.ui.debug("hdtv.drawable.DrawableCompound: firstID=" + str(firstID), level=6)
        return firstID
        

    def _lastID(self, onlyVisible = False):
        if onlyVisible:
            ids = list(self.visible)
        else:
            ids = self.keys()

        try:
            lastID = max(ids)
        except ValueError:
            lastID = self.activeID
            
        self._iteratorID = lastID
        hdtv.ui.debug("hdtv.drawable.DrawableCompound: lastID=" + str(lastID), level=6)
        return lastID
        
    
    def _nextID(self, onlyVisible = False):
        """
        Get next ID after _iteratorID
        """
        try:
            if onlyVisible:
                ids = list(self.visible)
            else:
                ids = self.keys()
                
            ids.sort()
            nextIndex = (ids.index(self._iteratorID) + 1) % len(ids)
            nextID = ids[nextIndex]

        except ValueError:
                nextID = self.activeID if not self.activeID is None else self.firstID 
            
        hdtv.ui.debug("hdtv.drawable.DrawableCompound: nextID="+ str(nextID), level=6)
        self._iteratorID = nextID
        return nextID
    
    @property
    def prevID(self):
        return self._prevID(onlyVisible = False)
    
    @property
    def prevVisibleID(self):
        return self._prevID(onlyVisible=True)
    
    def _prevID(self, onlyVisible=False):
        """
        Get previous ID before _iteratorID
        """
        try:
            if onlyVisible:
                ids = list(self.visible)
            else:
                ids = self.keys()
            
            ids.sort()
            prevIndex = (ids.index(self._iteratorID) - 1) % len(ids)
            prevID = ids[prevIndex]
        except ValueError:
            prevID = self.activeID if not self.activeID is None else self.lastID

        self._iteratorID = prevID
        hdtv.ui.debug("hdtv.drawable.DrawableCompound: prevID=" + str(prevID), level=6)
        return prevID

    def __getitem__(self, ID):
        return self.objects.__getitem__(ID)


    def __setitem__(self, ID, obj):
        """ 
        Low level function to add an object to this compound
        Note: This does not call Draw 
        """
        try:
            obj.SetID(ID)
        except AttributeError:
            pass
        self.objects.__setitem__(ID, obj)


    def __delitem__(self, ID):
        """
        Low level function to delete an object from this compound
        Note: This does not call Remove
        """
        if ID in self.visible:
            self.visible.discard(ID)
        if ID == self.activeID:
            self.activeID = None
        self.objects.__delitem__(ID)


    def keys(self):
        return self.objects.keys()
        
        
    def Index(self, obj):
        """
        Return index such that self.objects[index] == obj
        """
        index = [k for (k,v) in self.objects.iteritems() if v == obj]
        if len(index) == 0:
            raise ValueError, "Object not found in this collection"
        else:
            return index[0]

    def Add(self, obj):
        """
        Adds an object to the first free index (this also calls draw for the object)
        """
        ID = self.GetFreeID()
        hdtv.ui.debug("hdtv.drawable.DrawableCompound.Add(): setting _iteratorID to %d" % ID)
        self[ID] = obj
        if self.viewport:
            obj.SetColor(active=False)
            obj.Draw(self.viewport)
            self.visible.add(ID)
        return ID
        
    def Insert(self, obj, ID):
        """
        Inserts an object into the index at id ID, possibly removing an object
        which was there before. (This also calls draw for the object.)
        """
        if ID in self.keys():
            self.RemoveObjects([ID])
        
        self[ID] = obj
        if self.viewport:
            obj.Draw(self.viewport)
            self.visible.add(ID)
        return ID

    def GetFreeID(self):
        """
        Finds the first free index
        """
        # Find a free ID
        ID = 0
        while ID in self.keys():
            ID += 1
        return ID

    def PrintObject(self, ID, verbose=False, if_visible=False):
        """
        Print object properties
        """
        stat = " "
        visible = False
        obj = self.objects[ID]
        
        if ID == self.activeID:
            stat += "A"
            visible = True
        else:
            stat += " "
        if ID in self.visible:
            stat += "V"
            visible = True
        else:
            stat += " "
        if not if_visible or visible:
            try:
                print "%d %s %s" % (ID, stat, obj.formatted_str(verbose))
            except AttributeError:
                # just use normal str if no formatted_str function exists
                print "%d %s %s" % (ID, stat, obj)

    def ListObjects(self, verbose=False, visible_only=False):
        """
        List all objects in a human readable way
        """
        for ID in self.objects.keys():
            self.PrintObject(ID, verbose=verbose, if_visible=visible_only)
            
    def ActivateObject(self, ID=None):
        """
        Activates the object with id ID, while also highlighting it
        """
        self.viewport.LockUpdate()

        # set new active object
        if ID is None:
            # lowlight previously active object
            if not self.activeID is None:
                self.objects[self.activeID].SetColor(active=False)
            self.activeID=None
        elif ID in self.keys():
            if not self.activeID is None:
                self.objects[self.activeID].SetColor(active=False)
            self.objects[ID].SetColor(active=True)
            self.activeID = ID
            self.objects[ID].ToTop()
            if not ID in self.visible: # Show if not visible
                self.ShowObjects(ID)
        else:
            print "Warning, invalid id %s" %ID
        self.viewport.UnlockUpdate()
        
    def GetActiveObject(self):
        """
        Returns the presently active object
        """
    
        if self.activeID == None:
            return None
        else:
            return self.objects[self.activeID]
        
    def Draw(self, viewport):
        """
        Draw function
        """
        if not self.viewport == viewport:
            # Unlike the Display object of the underlying implementation,
            # python objects can only be drawn on a single viewport
            raise RuntimeError, "Object can only be drawn on a single viewport"
        self.viewport = viewport
        self.viewport.LockUpdate()
        for ID in self.iterkeys():
            self.objects[ID].Draw(self.viewport)
            self.visible.add(ID)
        self.viewport.UnlockUpdate()
    
    
    def Remove(self):
        """
        Remove 
        """
        self.RemoveAll()
        
    def RemoveAll(self):
        """
        Remove all 
        """
#        self.viewport.LockUpdate()
#        for ID in self.iterkeys():
#            if ID == self._iteratorID:
#                self._iteratorID = self.prevID
#            self.pop(ID).Remove()
#        self.viewport.UnlockUpdate()
        ids = self.iterkeys()
        self.RemoveObjects(ids)

    def RemoveObjects(self, ids):
        """
        Remove objects with the specified ids
        """
        self.viewport.LockUpdate()
        if isinstance(ids, int):
            ids = [ids]
        for ID in ids:
            try:
                if ID == self._iteratorID:
                    self._iteratorID = self.prevID 
                self.pop(ID).Remove()
            except KeyError:
                print "Warning: ID", str(ID), "not found"
        self.viewport.UnlockUpdate()


    def Refresh(self):
        """
        Refresh all objects
        """
        self.viewport.LockUpdate()
        for obj in self.itervalues():
            obj.Refresh()
        self.viewport.UnlockUpdate()
    
    def RefreshAll(self):
        """
        Refresh all - just a wrapper for convenience
        """
        self.Refresh()
    
    def RefreshObjects(self, ids):
        """
        Refresh objects with ids
        """
        self.viewport.LockUpdate()
        if isinstance(ids, int):
            ids = [ids]
        for ID in ids:
            try:
                self.objects[ID].Refresh
            except KeyError:
                print "Warning: ID %d not found" % ID
        self.viewport.UnlockUpdate()
    
    def RefreshVisible(self):
        """
        Refresh visible objects
        """
        self.RefreshObjects(self.visible)
    
    
    def Hide(self):
        """
        Hide the whole object
        """
        self.HideAll()
            
    def HideAll(self):
        """
        Hide all 
        """
        self.viewport.LockUpdate()
        for ID in self.iterkeys():
            if ID in self.visible:
                self.objects[ID].Hide()
        self.visible.clear()
        self.viewport.UnlockUpdate()
            
    def HideObjects(self, ids):
        """
        Hide objects from the display
        """
        self.viewport.LockUpdate()
        # if only one object is given
        if isinstance(ids, int):
            ids = [ids]
        for ID in ids:
            if ID in self.visible:
                try:
                    self.objects[ID].Hide()
                    self.visible.discard(ID)
                except KeyError:
                    print "Warning: ID %d not found" % ID
        self.viewport.UnlockUpdate()


    def Show(self):
        """
        Show the whole object
        """
        return self.ShowAll()
        
    def ShowAll(self):
        """
        Show all 
        """
        return self.ShowObjects(self.keys(), clear=True)
    
    def ShowObjects(self, ids, clear=True):
        """
        Show objects on the display. 

        If the clear parameter is True, the display is cleared first. 
        Otherwise the objects are shown in addition to the ones, that 
        are already visible.
        """
        self.viewport.LockUpdate()
        if isinstance(ids, int):
            ids = [ids]
        if clear:
            self.HideAll()
        for ID in ids:
            if ID not in self.visible:
                try:
                    self.objects[ID].Show()
                    self.visible.add(ID)
                except KeyError:
                    print "Warning: ID %s not found" % ID
                    
        # Check if active ID is still visible
        if self.activeID not in self.visible:
            self.ActivateObject(min(ids))
        
        self._iteratorID = min(ids)
        self.viewport.UnlockUpdate()
        return ids


    def isInVisibleRegion(self, ID):
        """
        Check if object is in the visible region of the viewport
        """
        xdim = self.objects[ID].xdimensions
        
        viewport_start = self.viewport.GetOffset()
        viewport_end = viewport_start + self.viewport.GetXVisibleRegion()

        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: object ID: %d" %ID, level=6)
        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: viewport_start %s, viewport_end %s" 
                       % (viewport_start, viewport_end), level=6)
        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: object %d, starts at %s and ends at %s" 
                       % (ID, xdim[0], xdim[1]), level=6)
            
        if (xdim[0] > viewport_start) and (xdim[1] < viewport_end):
            hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: ID %d is visible" % ID, level=4)
            return True
        else:
            hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: ID %d is *not* visible" % ID, level=4)
            return False
        
        
    def FocusObjects(self, ids):
        """
        Move and stretch viewport to show multiple objects
        """
        
        xdimensions = ()
        # Get dimensions of objects
        for ID in ids:
            xdimensions += self.objects[ID].xdimensions
            if ID not in self.visible:
                self.objects[ID].Show()
        
        self._iteratorID = min(ids)
        
        view_width = max(xdimensions) - min(xdimensions)
        view_width *= 1.2
        if view_width < 50.:
            view_width = 50. # TODO: make this configurable
        view_center = (max(xdimensions) + min(xdimensions)) / 2.
        
        self.viewport.SetXVisibleRegion(view_width)
        self.viewport.SetXCenter(view_center)
    
    
    def FocusObject(self, ID=None):
        """
        If ID is not given: Focus active object
        """
        if ID is None:
            ID = self.activeID
        
        if ID is None:
            hdtv.ui.error("No active object")
            return
        self.FocusObjects([ID])
        
    def ShowNext(self, nb=1):
        """
        Show next object (by index)

        With the parameter nb, the user can choose how many new spectra
        there should be displayed.
        """
        if nb > len(self.objects):
            self.ShowAll()
            return
        if len(self.visible)==0 or len(self.visible)==len(self.objects):
            self.ShowFirst(nb)
            return
        ids = self.keys()
        ids.sort()
        index = ids.index(max(self.visible))
        ids = ids[index+1:index+nb+1]
        if len(ids)==0:
            return self.ShowFirst(nb)
        self.ShowObjects(ids, clear=True)
        return ids

    def ShowPrev(self, nb=1):
        """
        Show previous object (by index)

        With the parameter nb, the user can choose how many new spectra
        there should be displayed.
        """
        if nb > len(self.objects):
            self.ShowAll()
            return
        if len(self.visible)==0 or len(self.visible)==len(self.objects):
            self.ShowLast(nb)
            return
        ids = self.keys()
        ids.sort()
        index = ids.index(min(self.visible))
        if nb > index:
            ids = ids[0:index]
        else:
            ids = ids[index-nb:index]
        if len(ids)==0:
            self.ShowLast(nb)
            return
        self.ShowObjects(ids, clear=True)
        return ids
    
    def ShowFirst(self, nb=1):
        """
        Show the first nb objects
        """
        if nb > len(self.objects):
            return self.ShowAll()
        ids = self.keys()
        ids.sort()
        ids = ids[:nb]
        self.ShowObjects(ids, clear=True)
        return ids

    def ShowLast(self, nb=1):
        """
        Show the last nb objects
        """
        if nb > len(self.objects):
            self.ShowAll()
            return
        ids = self.keys()
        ids.sort()
        ids = ids[len(ids)-nb:]
        self.ShowObjects(ids, clear=True)
        return ids
        
    def SetColor(self, color=None, active=False):
        """
        Call SetColor for all components
        """
        self.viewport.LockUpdate()
        for obj in self.itervalues():
            obj.SetColor(color, active)
        self.viewport.UnlockUpdate()
        
    def SetCal(self, cal):
        """
        Call SetCal for all components
        """
        self.viewport.LockUpdate()
        for obj in self.itervalues():
            obj.SetCal(cal)
        self.viewport.UnlockUpdate()
            

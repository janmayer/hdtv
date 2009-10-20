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

import hdtv.cal
import hdtv.color
import hdtv.ui


class Drawable(object):
    def __init__(self, color=None, cal=None):
        self.viewport = None
        # displayObj will be created when calling Draw
        self.displayObj = None
        self.active = False
        self.cal = cal
        self.color = color
        self.ID = None
       
    def __str__(self):
        return str(self.displayObj)

    # cal property
    def _set_cal(self, cal):
        self._cal=hdtv.cal.MakeCalibration(cal)
        # update display if needed
        try:
            self.displayObj.SetCal(self._cal)
        except:
            pass
        
    def _get_cal(self):
        return self._cal
        
    cal = property(_get_cal, _set_cal)
    
    # color property
    def _set_color(self, color):
        self._activeColor = hdtv.color.Highlight(color, active=True)
        self._passiveColor = hdtv.color.Highlight(color, active=False)
        # update display if needed
        if not self.displayObj is None:
            if self._active:
                self.displayObj.SetColor(self._activeColor)
            else:
                self.displayObj.SetColor(self._passiveColor)
   
    def _get_color(self):
        return self._passiveColor
        
    color = property(_get_color, _set_color)
    
    # active property
    def _set_active(self, state):
        self._active = state
        if not self.displayObj is None:
            if self._active:
                self.displayObj.SetColor(self._activeColor)
                # move the object to the top of its draw stack
                try:
                    self.displayObj.ToTop()
                except:
                    pass
            else:
                self.displayObj.SetColor(self._passiveColor)
                
    def _get_active(self):
        return self._active
        
    active = property(_get_active, _set_active)
    
    # ID property
    def _set_ID(self, ID):
        self._ID = ID
        if self.displayObj:
            try:
                self.displayObj.SetID(ID)
            except:
                pass
    
    def _get_ID(self):
        return self._ID
        
    ID = property(_get_ID, _set_ID)
    
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
        Refresh the objects data 
        """
        pass


    def Show(self):
        """
        Show the object 
        """
        if not self.viewport:
            return
        if self.displayObj:
            if self.active:
                self.displayObj.SetColor(self._activeColor)
                # move the object to the top of its draw stack
                try:
                    self.displayObj.ToTop()
                except:
                    pass
            else:
                self.displayObj.SetColor(self._passiveColor)
            if self.cal:
                self.displayObj.SetCal(self.cal)
            self.displayObj.Show()

    def Hide(self):
        """
        Hide the object 
        """
        if not self.viewport:
            return
        if self.displayObj:
            self.displayObj.Hide()


class DrawableManager(object):
    """
    This class provides some handy functions to manage a collection of 
    identical drawable objects.
    """
    def __init__(self, viewport=None):
        self.viewport = viewport
        # dictionary to store the drawable objects
        self.dict = dict()
        self.visible = set()
        self.activeID = None
        # This should keep track of ID for nextID, prevID
        self._iteratorID = self.activeID 
        self._active = False
    
    def __len__(self):
        return len(self.dict)
        
    @property
    def ids(self):
        return self.dict.keys()
    
    # active property
    def _set_active(self, state):
        self._active = state
        if self.activeID is not None:
            # give state to the active child
            self.GetActiveObject().active=state
        
    def _get_active(self):
        return self._active
        
    active = property(_get_active, _set_active)

    def ActivateObject(self, ID=None):
        """
        Activates the object with id ID
        """
        if ID is not None and ID not in self.ids:
            raise KeyError
        if self.viewport:
            self.viewport.LockUpdate()
        # change state of former active object
        if self.activeID is not None:
            self.GetActiveObject().active = False
        # activate new object
        self.activeID = ID
        if self.activeID is not None:
            # reset iterator
            self._iteratorID = self.activeID 
            # change state of object
            self.GetActiveObject().active = self.active
            # call ShowObject, to make sure the new active object is visible
            self.ShowObjects(ID, clear=False)
        if self.viewport:
            self.viewport.UnlockUpdate()
 
    def GetActiveObject(self):
        """
        Returns currently active object
        """
        if self.activeID is None:
            return None
        else:
            return self.dict[self.activeID]


    def Index(self, obj):
        """
        Return index such that self[index] == obj
        """
        index = [k for (k,v) in self.dict.iteritems() if v == obj]
        if len(index) == 0:
            raise ValueError, "Object not found in this collection"
        else:
            return index[0]


    def Insert(self, obj, ID=None):
        """
        This inserts an object to the dictionary of this manager
        If no ID is given, the first free ID is used, else the object is inserted
        at the given ID, possibly removing an object which was there before. 
        """
        # if no ID is specified we take the first free ID
        if ID is None:
            ID = self.GetFreeID()
        self._iteratorID = ID
        self.dict[ID] = obj
        obj.ID = ID
        if self.viewport:
            obj.Draw(self.viewport)
            self.visible.add(ID)
        return ID

    def Pop(self, ID):
        """
        Remove object with ID
        """
        if ID == self.activeID:
            self.ActivateObject(None)
        if ID == self._iteratorID:
            # set iterator to the ID before the one we remove
            self._iteratorID = self.prevID 
        try:
            self.dict.pop(ID)
        except KeyError:
            hdtv.ui.warn("Warning: ID %s not found." % ID)


    def Clear(self):
        """
        Clear dict and reset everything
        """
        self.activeID = None
        self._iterator = self.activeID
        self._active = False
        self.HideAll()
        self.dict.clear()


    def GetFreeID(self):
        """
        Finds the first free index
        """
        # Find a free ID
        ID = 0
        while ID in self.dict.iterkeys():
            ID += 1
        return ID


    # FIXME: this seems not to be used anymore (see SpecInterface)
    def PrintObject(self, ID, verbose=False, if_visible=False):
        """
        Print object properties
        """
        stat = " "
        visible = False
        obj = self.dict[ID]
        
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
                hdtv.ui.msg("%d %s %s" % (ID, stat, obj.formatted_str(verbose)))
            except AttributeError:
                # just use normal str if no formatted_str function exists
                hdtv.ui.msg("%d %s %s" % (ID, stat, obj))

    def ListObjects(self, verbose=False, visible_only=False):
        """
        List all objects in a human readable way
        """
        for ID in self.dict.keys():
            self.PrintObject(ID, verbose=verbose, if_visible=visible_only)


    def Draw(self, viewport):
        """
        Draw function (sets the viewport and draws all components)
        """
        if not self.viewport is None and not self.viewport == viewport:
            # Unlike the Display object of the underlying implementation,
            # python objects can only be drawn on a single viewport
            raise RuntimeError, "Object can only be drawn on a single viewport"
        self.viewport = viewport
        self.viewport.LockUpdate()
        for ID in self.dict.iterkeys():
            self.dict[ID].Draw(self.viewport)
            self.visible.add(ID)
        self.viewport.UnlockUpdate()
       

    # Refresh commands
    def Refresh(self):
        """
        Refresh whole object
        """
        return self.RefreshAll()
        
    def RefreshAll(self):
        """
        Refresh all objects in dict
        """
        return self.RefreshObjects(self.dict.iterkeys())
        
    def RefreshVisible(self):
        """
        Refresh visible objects
        """
        return self.RefreshObjects(self.visible)
    
    def RefreshObjects(self, ids):
        """
        Refresh objects with ids
        """
        if self.viewport:
            self.viewport.LockUpdate()
        if isinstance(ids, int):
            ids = [ids]
        for ID in ids:
            try:
                self.dict[ID].Refresh
            except KeyError:
                hdtv.ui.error("Warning: ID %d not found" % ID)
        if self.viewport:
            self.viewport.UnlockUpdate()
        return ids


    # Hide commands
    def Hide(self):
        """
        Hide the object as a whole (with info about current visible/active states)
        """
        # do not call HideAll here, as then we loose the info about 
        # visible/active states of the objects
        for obj in self.dict.itervalues():
            obj.Hide()
        
    def HideAll(self):
        """
        Hide all child objects
        """
        return self.HideObjects(self.dict.keys())

    def HideObjects(self, ids):
        """
        Hide objects
        """
        if self.viewport is None:
            return
        self.viewport.LockUpdate()
        # check if ids is list/iterable or just single id 
        try: iter(ids)
        except TypeError:
            ids = [ids]
        for ID in ids:
            if ID in self.visible:
                try:
                    self.dict[ID].Hide()
                    self.visible.discard(ID)
                except KeyError:
                    hdtv.ui.warn("ID %d not found" % ID)
        self.viewport.UnlockUpdate()
        return ids


    # Show commands:
    def Show(self):
        """
        Show the object as whole (according to last visible/active states)
        """
        self.ShowObjects(self.visible)
        if self.activeID is not None:
            self.GetActiveObject().active=self.active
        
    def ShowAll(self):
        """
        Show all 
        """
        return self.ShowObjects(self.dict.keys())
    
    def ShowObjects(self, ids, clear=True):
        """
        Show objects on the display. 

        If the clear parameter is True, the display is cleared first. 
        Otherwise the objects are shown in addition to the ones, that 
        are already visible.
        """
        if self.viewport is None:
            return
        self.viewport.LockUpdate()
        # check if ids is list/iterable or just single id 
        try: iter(ids)
        except TypeError:
            ids = [ids]
        if clear:
            # hide all other objects except in ids
            # do not use HideAll, because if the active objects is among 
            # the objects that should be shown, its state would be lost
            others = set(self.dict.keys())-set(ids)
            self.HideObjects(others)
        for ID in ids:
            try:
                self.dict[ID].Show()
                self.visible.add(ID)
            except KeyError:
                hdtv.ui.warn("ID %s not found" % ID)
        self.viewport.UnlockUpdate()
        return ids

# FIXME: does this belong here?
#    def isInVisibleRegion(self, ID):
#        """
#        Check if object is in the visible region of the viewport
#        """
#        if self.viewport is None: return False
#        xdim = self[ID].xdimensions
#        if xdim is None: # Object has no dimensions
#            return True
#        # get viewport limits
#        viewport_start = self.viewport.GetOffset()
#        viewport_end = viewport_start + self.viewport.GetXVisibleRegion()
#        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: object ID: %d" %ID, level=6)
#        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: viewport_start %s, viewport_end %s" 
#                       % (viewport_start, viewport_end), level=6)
#        hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: object %d, starts at %s and ends at %s" 
#                       % (ID, xdim[0], xdim[1]), level=6)
#        # do the check
#        if (xdim[0] > viewport_start) and (xdim[1] < viewport_end):
#            hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: ID %d is visible" % ID, level=4)
#            return True
#        else:
#            hdtv.ui.debug("hdtv.drawable.isInVisibleRegion: ID %d is *not* visible" % ID, level=4)
#            return False
#
#    def FocusObjects(self, ids):
#        """
#        Move and stretch viewport to show multiple objects
#        """
#        if self.viewport is None:
#            return
#        xdimensions = ()
#        # Get dimensions of objects
#        for ID in ids:
#            if self[ID].xdimensions is not None:
#                xdimensions += self[ID].xdimensions
#            if ID not in self.visible:
#                self[ID].Show()
#        self._iteratorID = min(ids)
#        # calulate
#        if len(xdimensions) > 0: 
#            view_width = max(xdimensions) - min(xdimensions)
#            view_width *= 1.2
#            if view_width < 50.:
#                view_width = 50. # TODO: make this configurable
#            view_center = (max(xdimensions) + min(xdimensions)) / 2.
#            # change viewport
#            self.viewport.SetXVisibleRegion(view_width)
#            self.viewport.SetXCenter(view_center)
#    
#    
#    def FocusObject(self, ID=None):
#        """
#        If ID is not given: Focus active object
#        """
#        if ID is None:
#            ID = self.activeID
#        if ID is None:
#            hdtv.ui.error("No active object")
#            return
#        self.FocusObjects([ID])
        
    
    # nextID/prevID/firstID/lastID getter
    @property
    def nextID(self):
        return self._nextID(onlyVisible = False)
    
    @property
    def nextVisibleID(self):
        return self._nextID(onlyVisible = True)
        
    @property
    def prevID(self):
        return self._prevID(onlyVisible = False)
    
    @property
    def prevVisibleID(self):
        return self._prevID(onlyVisible=True)

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
            ids = self.dict.keys()

        try:
            firstID = min(ids)
        except ValueError:
            firstID = self.activeID
        
        self._iteratorID = firstID
        hdtv.ui.debug("hdtv.drawable.DrawableManager: firstID=" + str(firstID), level=6)
        return firstID
        

    def _lastID(self, onlyVisible = False):
        if onlyVisible:
            ids = list(self.visible)
        else:
            ids = self.dict.keys()

        try:
            lastID = max(ids)
        except ValueError:
            lastID = self.activeID
            
        self._iteratorID = lastID
        hdtv.ui.debug("hdtv.drawable.DrawableManager: lastID=" + str(lastID), level=6)
        return lastID
        
    
    def _nextID(self, onlyVisible = False):
        """
        Get next ID after _iteratorID
        """
        try:
            if onlyVisible:
                ids = list(self.visible)
            else:
                ids = self.dict.keys()
                
            ids.sort()
            nextIndex = (ids.index(self._iteratorID) + 1) % len(ids)
            nextID = ids[nextIndex]

        except ValueError:
                nextID = self.activeID if not self.activeID is None else self.firstID 
            
        hdtv.ui.debug("hdtv.drawable.DrawableManager: nextID="+ str(nextID), level=6)
        self._iteratorID = nextID
        return nextID
    
    def _prevID(self, onlyVisible=False):
        """
        Get previous ID before _iteratorID
        """
        try:
            if onlyVisible:
                ids = list(self.visible)
            else:
                ids = self.dict.keys()
            
            ids.sort()
            prevIndex = (ids.index(self._iteratorID) - 1) % len(ids)
            prevID = ids[prevIndex]
        except ValueError:
            prevID = self.activeID if not self.activeID is None else self.lastID

        self._iteratorID = prevID
        hdtv.ui.debug("hdtv.drawable.DrawableManager: prevID=" + str(prevID), level=6)
        return prevID

    def ShowNext(self, nb=1):
        """
        Show next object (by index)

        With the parameter nb, the user can choose how many new spectra
        there should be displayed.
        """
        if nb > len(self.dict):
            self.ShowAll()
            return
        ids = self.dict.keys()
        index = ids.index(self.nextID)
        ids = ids[index:index+nb]
        self.ShowObjects(ids, clear=True)
        return ids

    def ShowPrev(self, nb=1):
        """
        Show previous object (by index)

        With the parameter nb, the user can choose how many new spectra
        there should be displayed.
        """
        if nb > len(self.dict):
            self.ShowAll()
            return
        ids = self.dict.keys()
        index = ids.index(self.prevID)
        ids = ids[index:index+nb]
        self.ShowObjects(ids, clear=True)
        return ids
     
    def ShowFirst(self, nb=1):
        """
        Show the first nb objects
        """
        if nb > len(self.dict):
            return self.ShowAll()
        ids = self.dict.keys()
        ids.sort()
        ids = ids[:nb]
        self.ShowObjects(ids, clear=True)
        return ids

    def ShowLast(self, nb=1):
        """
        Show the last nb objects
        """
        if nb > len(self.dict):
            self.ShowAll()
            return
        ids = self.dict.keys()
        ids.sort()
        ids = ids[len(ids)-nb:]
        self.ShowObjects(ids, clear=True)
        return ids
        


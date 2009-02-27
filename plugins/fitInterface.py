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
import hdtv.cmdline
import hdtv.cmdhelper

from hdtv.drawable import DrawableCompound
from hdtv.marker import Marker
from hdtv.fitter import Fitter
from hdtv.fit import Fit


class SpectrumCompound(DrawableCompound):
	""" 
	This CompoundObject is a dictionary of Fits belonging to a spectrum.
	Everything that is not directed at the Fit dict is dispatched to the 
	underlying spectrum. Thus from the outside this can be treated as an 
	spectrum object, so that everything that has been written with a 
	spectrum object in mind will continue to work. 
	"""
	def __init__(self, viewport, spec):
		DrawableCompound.__init__(self,viewport)
		self.spec = spec
		self.color = spec.color
		self.pendingFit=None
		
	def __getattr__(self, name):
		"""
		Dispatch everything which is unknown to this object to the spectrum
		"""
		return getattr(self.spec, name)

	def Refresh(self):
		"""
		Refresh spectrum and fits
		"""
		self.spec.Refresh()
		DrawableCompound.Refresh(self)
		if self.pendingFit:
			self.pendingFit.Refresh()
		
	def Draw(self, viewport):
		"""
		Draw spectrum and fits
		"""
		self.spec.Draw(viewport)
		DrawableCompound.Draw(self, viewport)
		if self.pendingFit:
			self.pendingFit.Draw(viewport)
		
	def Show(self):
		"""
		Show the spectrum and all fits that are marked as visible
		"""
		self.spec.Show()
		# only show objects that have been visible before
		for i in list(self.visible):
			self.objects[i].Show()
		if self.pendingFit:
			self.pendingFit.Show()
			
	def ShowAll(self):
		"""
		Show spectrum and all fits
		"""
		DrawableCompound.ShowAll(self)
		
	def Remove(self):
		"""
		Remove spectrum and fits
		"""
		self.spec.Remove()
		DrawableCompound.Remove(self)
		if self.pendingFit:
			self.pendingFit.Remove()
		
	def Hide(self):
		"""
		Hide the whole object,
		but remember which fits were visible
		"""
		# remove pending Fit
		if self.pendingFit:
			self.pendingFit.Remove()
			self.pendingFit = None
		# hide the spectrum itself
		self.spec.Hide()
		# Hide all fits, but remember what was visible
		visible = self.visible.copy()
		DrawableCompound.Hide(self)
		self.visible = visible
		
	def HideAll(self):
		"""
		Hide only the fits
		"""
		DrawableCompound.HideAll(self)

	def SetCal(self, cal):
		self.spec.SetCal(cal)
		DrawableCompound.SetCal(self, cal)
		if self.pendingFit:
			self.pendingFit.SetCal(cal)


class FitInterface:
	"""
	User interface for fitting 1-d spectra
	"""
	def __init__(self, window, spectra):
		print "Loaded user interface for fitting of 1-d spectra"
		self.window = window
		self.spectra = spectra

		self.peakModel= "theuerkauf"
		self.bgDegree = 1
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []

		# tv commands
		self.tv = TvFitInterface(self)

		# Register hotkeys
		self.window.AddHotkey(ROOT.kKey_b, self._PutBackgroundMarker)
		self.window.AddHotkey(ROOT.kKey_r, self._PutRegionMarker)
		self.window.AddHotkey(ROOT.kKey_p, self._PutPeakMarker)
#		self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_p], self._DeletePeakMarker)
		self.window.AddHotkey(ROOT.kKey_B, self.FitBackground)
		self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_B], self.ClearBackground)
	  	self.window.AddHotkey(ROOT.kKey_F, self.FitPeaks)
	  	self.window.AddHotkey([ROOT.kKey_Plus, ROOT.kKey_F], self.KeepFit)
	  	self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.ClearFit)
#	  	self.window.AddHotkey(ROOT.kKey_I, self.Integrate)
	  	self.window.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
	  	self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D], lambda: self.SetDecomp(False))
		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_s],
				lambda: self.window.EnterEditMode(prompt="Show Fit: ",
		                                   handler=self._HotkeyShow))
		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_a],
		        lambda: self.window.EnterEditMode(prompt="Activate Fit: ",
		                                   handler=self._HotkeyActivate))
		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_p], self._HotkeyShowPrev)
		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_n], self._HotkeyShowNext)


	def _HotkeyShowPrev(self):
		"""
		ShowPrev wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.fViewport.SetStatusText("No active spectrum")
			return
		try:
			self.spectra[self.spectra.activeID].ShowPrev()
		except AttributeError:
			self.window.fViewport.SetStatusText("No fits available")
			
			
	def _HotkeyShowNext(self):
		"""
		ShowNext wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.fViewport.SetStatusText("No active spectrum")
			return
		try:
			self.spectra[self.spectra.activeID].ShowNext()
		except AttributeError:
			self.window.fViewport.SetStatusText("No fits available")
			
			
	def _HotkeyShow(self, arg):
		"""
		Show wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.fViewport.SetStatusText("No active spectrum")
			return
		try:
			ids = [int(a) for a in arg.split()]
			self.spectra[self.spectra.activeID].ShowObjects(ids)
		except ValueError:
			self.window.fViewport.SetStatusText("Invalid fit identifier: %s" % arg)

	def _HotkeyActivate(self, arg):
		"""
		ActivateObject wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.fViewport.SetStatusText("No active spectrum")
			return
		try:
			ID = int(arg)
			self.spectra[self.spectra.activeID].ActivateObject(ID)
		except ValueError:
			self.window.fViewport.SetStatusText("Invalid fit identifier: %s" % arg)
		except KeyError:
			self.window.fViewport.SetStatusText("No such id: %d" % ID)


	def _PutRegionMarker(self):
		"""
		Put a region marker at the current cursor position (internal use only)
		"""
		# FIXME: code very similar to the other put marker functions
		if not self.spectra.activeID==None:
			specID = self.spectra.activeID
			try:
				self.spectra[specID].pendingFit
			except AttributeError:
				pass
			else:
				if self.spectra[specID].pendingFit:
					self.CopyMarkers(self.spectra[specID].pendingFit)
					self.spectra[specID].pendingFit.Remove()
					self.spectra[specID].pendingFit = None
			try:
				self.spectra[specID].activeID
			except AttributeError:
				pass
			else:
				if not self.spectra[specID].activeID==None:
					fitID = self.spectra[specID].activeID
					self.CopyMarkers(self.spectra[specID][fitID])
					self.spectra[specID].HideObjects(fitID)
		self.window.PutPairedMarker("X", "REGION", self.activeRegionMarkers, 1)	
			
			
	def _PutBackgroundMarker(self):
		"""
		Put a background marker at the current cursor position (internal use only)
		"""
		# FIXME: code very similar to the other put marker functions
		if not self.spectra.activeID==None:
			specID = self.spectra.activeID
			try:
				self.spectra[specID].pendingFit
			except AttributeError:
				pass
			else:
				if self.spectra[specID].pendingFit:
					self.CopyMarkers(self.spectra[specID].pendingFit)
					self.spectra[specID].pendingFit.Remove()
					self.spectra[specID].pendingFit = None
			try:
				self.spectra[specID].activeID
			except AttributeError:
				pass
			else:
				if not self.spectra[specID].activeID==None:
					fitID = self.spectra[specID].activeID
					self.CopyMarkers(self.spectra[specID][fitID])
					self.spectra[specID].HideObjects(fitID)
		self.window.PutPairedMarker("X", "BACKGROUND", self.activeBgMarkers)
		
		
	def _PutPeakMarker(self):
		"""
		Put a peak marker at the current cursor position (internal use only)
		"""
		# FIXME: code very similar to the other put marker functions
		if not self.spectra.activeID==None:
			specID = self.spectra.activeID
			try:
				self.spectra[specID].pendingFit
			except AttributeError:
				pass
			else:
				if self.spectra[specID].pendingFit:
					self.CopyMarkers(self.spectra[specID].pendingFit)
					self.spectra[specID].pendingFit.Remove()
					self.spectra[specID].pendingFit = None
			try:
				self.spectra[specID].activeID
			except AttributeError:
				pass
			else:
				if not self.spectra[specID].activeID==None:
					fitID = self.spectra[specID].activeID
					self.CopyMarkers(self.spectra[specID][fitID])
					self.spectra[specID].HideObjects(fitID)
		pos = self.window.fViewport.GetCursorX()
  		self.activePeakMarkers.append(Marker("PEAK", pos))
  		self.activePeakMarkers[-1].Draw(self.window.fViewport)



	def FitBackground(self):
		"""
		Fit the background
		
		This only fits the background with a polynom of self.bgDegree
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return
		spec = self.spectra[self.spectra.activeID]
		try:
			fit = self.spectra[self.spectra.activeID].pendingFit
		except AttributeError:
			# create SpectrumCompound object 
			spec = SpectrumCompound(self.window.fViewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
			self.spectra[self.spectra.activeID]=spec
			fit = None
		if not fit:
			fitter = Fitter(spec.spec, self.peakModel, self.bgDegree)
			fit = Fit(fitter, self.activeRegionMarkers, self.activePeakMarkers, 
							  self.activeBgMarkers, color=spec.color, cal=spec.cal)
		fit.FitBgFunc()
		fit.Draw(self.window.fViewport)
		self.spectra[self.spectra.activeID].pendingFit = fit
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []

	def FitPeaks(self):
		"""
		Fit the peak
		
		If there are background markers, a background fit it included.
		"""
		# get active spectrum
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		try:
			# check if it is already a SpectrumCompound object
			fit = self.spectra[self.spectra.activeID].pendingFit
		except AttributeError:
			# create SpectrumCompound object 
			spec = SpectrumCompound(self.window.fViewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
			self.spectra[self.spectra.activeID]=spec
			fit = None
		if not fit:
			# create fresh fit
			fitter = Fitter(spec.spec, self.peakModel, self.bgDegree)
			fit = Fit(fitter, self.activeRegionMarkers, self.activePeakMarkers, 
							  self.activeBgMarkers, color=spec.color, cal=spec.cal)
		if len(fit.bgMarkers)>0:
			fit.FitBgFunc()
		fit.FitPeakFunc()
		fit.Draw(self.window.fViewport)
		self.spectra[self.spectra.activeID].pendingFit = fit
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []


	def ActivateFit(self, ID):
		"""
		Activate one fit
		
		The markers of a activated fit, can be changed and then the fit 
		can be repeated. If the user decided to keep the new fit, the old 
		fit will be replaced.
		"""
		try:
			spec = self.spectra[self.spectra.activeID]
			spec.ActivateObject(ID)
		except KeyError:
			print 'There is no active spectrum'
		except AttributeError:
			print 'There are no fits for this spectrum'


	def KeepFit(self):
		"""
		Keep this fit, 
		
		If there is an activated fit, it will be replaced by the new fit.
		"""
		# get active spectrum
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if not spec.pendingFit:
			if len(self.activeRegionMarkers)+len(self.activePeakMarkers)>0:
				self.FitPeaks()
			else:
				print "Warning: No Fit available, no action taken"
				return
		fitID = spec.activeID
		if fitID==None:
			fitID = spec.GetFreeID()
		else:
			spec[fitID].Remove()
		# FIXME: we need SetColor for markers!
		spec.pendingFit.SetColor(spec.color)
		spec[fitID] = spec.pendingFit
		spec.pendingFit = None
		spec.activeID = None


	def ClearFit(self):
		"""
		Clear all fit markers and the pending fit, if there is one
		"""
		# remove all markers
		markers = self.activePeakMarkers+self.activeRegionMarkers+self.activeBgMarkers
		for marker in markers:
			marker.Remove()
		self.activePeakMarkers=[]
		self.activeRegionMarkers=[]
		self.activeBgMarkers=[]
		# remove pending fit, if there is any
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if hasattr(spec, 'pendingFit') and spec.pendingFit:
			spec.pendingFit.Remove()
			spec.pendingFit = None
		
		
	def ClearBackground(self):
		"""
		Clear Background markers and fit
		If there is a pending peak fit, it is repeated without the background
		"""
		# remove background markers
		for marker in self.activeBgMarkers:
			marker.Remove()
		self.activeBgMarkers=[]
		if self.spectra.activeID==None:
			return 
		spec = self.spectra[self.spectra.activeID]
		# adjust pending fit, if needed
		if hasattr(spec, 'pendingFit') and spec.pendingFit:
			if spec.pendingFit.dispPeakFunc:
				# redo PeakFit without Background
				self.CopyMarkers(spec.pendingFit)
				spec.pendingFit.Remove()
				spec.pendingFit = None
				# delete the background markers of the pending fit
				for marker in self.activeBgMarkers:
					marker.Remove()
				self.activeBgMarkers=[]
				self.FitPeaks()
			else: 
				# remove pending fit as it doesn't contain a peak fit
				spec.pendingFit.Remove()
				spec.pendingFit = None		
				
	
	def CopyMarkers(self, fit):
		"""
		Copy markers from a fit object to the activeMarkers lists
		"""
		self.activeRegionMarkers = []
		for marker in fit.regionMarkers:
			self.activeRegionMarkers.append(marker.Copy(cal=None))
		self.activePeakMarkers = []
		for marker in fit.peakMarkers:
			self.activePeakMarkers.append(marker.Copy(cal=None))
		self.activeBgMarkers = []
		for marker in fit.bgMarkers:
			self.activeBgMarkers.append(marker.Copy(cal=None))
		self.window.fViewport.LockUpdate()
		markers = self.activeRegionMarkers+self.activePeakMarkers+self.activeBgMarkers
		for marker in markers:
			marker.Draw(self.window.fViewport)
		self.window.fViewport.UnlockUpdate()
		

	def SetDecomp(self, stat=True):
		"""
		Show peak decomposition
		"""
		# get active spectrum
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		try:
			fit = spec.pendingFit
			if not fit:
				fit = spec[spec.activeID]
			fit.SetDecomp(stat)
		except AttributeError:
			print "No fits availabel, no action taken."
		except KeyError:
			print "No active fit."


	def SetBgDeg(self, bgdeg):
		self.bgDegree = bgdeg
		if self.spectra.activeID==None:
			return
		spec = self.spectra[self.spectra.activeID]
		if hasattr(spec, 'pendingFit') and spec.pendingFit:
			spec.pendingFit.fitter.bgdeg = bgdeg
			spec.pendingFit.Refresh()
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()

#	def ShowFitOptions(self):
#		print self.peakmodel.OptionsStr()
	

class TvFitInterface:
	"""
	TV style interface for fitting
	"""
	def __init__(self, fitInterface):
		self.fitIf = fitInterface
		self.spectra = self.fitIf.spectra

		# register tv commands
		hdtv.cmdline.AddCommand("fit list", self.FitList, nargs=0)
		hdtv.cmdline.AddCommand("fit show", self.FitShow, minargs=1)
		hdtv.cmdline.AddCommand("fit delete", self.FitDelete, minargs=1)
		hdtv.cmdline.AddCommand("fit activate", self.FitActivate, nargs=1)
		hdtv.cmdline.AddCommand("fit param background degree", self.FitParamBgDeg, nargs=1)
		hdtv.cmdline.AddCommand("fit param status", self.FitParamStatus, nargs=0)
#		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)
#		hdtv.cmdline.AddCommand("fit function peak activate", self.FitSetPeakModel,
#								completer=self.PeakModelCompleter, nargs=1)

		hdtv.cmdline.AddCommand("calibration position assign", self.CalPosAssign, minargs=2)

	def FitList(self, args):
		"""
		Print a list of all fits belonging to the active spectrum 
		"""
		try:
			spec = self.spectra[self.spectra.activeID]
			if self.spectra.activeID in self.spectra.visible:
				visible = True
			else:
				visible = False
			print 'Fits belonging to %s (visible=%s):' %(str(spec), visible)
			spec.ListObjects()
		except KeyError:
			print "No active spectrum"
			return False
		except AttributeError:
			print "There are no fits for this spectrum"
			return False
		except:
			print "Usage: fit list"
			return False	
		
	def FitDelete(self, args):
		""" 
		Delete fits
		"""
		try:
			ids = hdtv.cmdhelper.ParseRange(args)
			if ids == "NONE":
				return
			elif ids == "ALL":
				ids = self.spectra[self.spectra.activeID].keys()
			self.spectra[self.spectra.activeID].RemoveObjects(ids)
		except KeyError:
			print "No active spectrum"
			return False
		except AttributeError:
			print "There are no fits for this spectrum"
			return False
		except:
			print "Usage: spectrum delete <ids>|none|all"
			return False
	
	def FitShow(self, args):
		"""
		Show Fits
		"""
		try:
			ids = hdtv.cmdhelper.ParseRange(args)
			if not self.spectra.activeID in self.spectra.visible:
				print "Warning: active spectrum is not visible, no action taken"
				return True
			if ids == "NONE":
				self.spectra[self.spectra.activeID].HideAll()
			elif ids == "ALL":
				self.spectra[self.spectra.activeID].ShowAll()
			else:
				self.spectra[self.spectra.activeID].ShowObjects(ids)
		except KeyError:
			print "No active spectrum"
			return False
		except AttributeError:
			print "There are no fits for this spectrum"
			return False
		except: 
			print "Usage: spectrum show <ids>|all|none"
			return False
	
	def FitActivate(self, args):
		"""
		Activate one spectra
		"""
		try:
			ID = hdtv.cmdhelper.ParseRange(args)
			if ID=="NONE":
				ID = None
			else:
				ID = int(args[0])
			self.fitIf.ActivateFit(ID)
		except ValueError:
			print "Usage: fit activate <id>|none"
			return False


	def FitParamBgDeg(self, args):
		try:
			bgdeg = int(args[0])
		except ValueError:
			print "Usage: fit parameter background degree <deg>"
			return False
		self.fitIf.SetBgDeg(bgdeg)

	def FitParamStatus(self, args):
		self.fitIf.ShowFitOptions()


	def CalPosAssign(self, args):
		""" 
		Calibrate the active spectrum by asigning energies to fitted peaks

		Peaks are specified by their id and the peak number within the peak.
		Syntax: id.number
		If no number is given, the first peak in the fit is used.
		"""
		if self.spectra.activeID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		spec = self.spectra[self.spectra.activeID]
		try:
			if len(args)%2 !=0:
				raise ValueError
			channels = []
			energies = []
			while len(args)>0:
				fitID = args.pop(0).split('.')
				if len(fitID)>2:
					raise ValueError
				elif len(fitID)==2:
					channel = spec[int(fitID[0])].peakMarkers[int(fitID[1])].p1
				else:
					channel = spec[int(fitID[0])].peakMarkers[0].p1				 	
				channels.append(channel)
				energies.append(float(args.pop(0)))
			pairs = zip(channels, energies)
			cal = hdtv.cal.CalFromPairs(pairs)
		except (ValueError, KeyError):
			print "Usage: calibration position set <f1>[.?] <e1> <f2>[.?] <e2> "
			return False
		else:
			pairs = zip(channels, energies)
			cal = hdtv.cal.CalFromPairs(pairs)
			spec.SetCal(cal)
			self.fitIf.window.Expand()
			return True
		



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
from hdtv.marker import MarkerCollection
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
		
		
	def Draw(self, viewport):
		"""
		Draw spectrum and fits
		"""
		self.spec.Draw(viewport)
		DrawableCompound.Draw(self, viewport)
		
		
	def Show(self):
		"""
		Show the spectrum and all fits that are marked as visible
		"""
		self.spec.Show()
		# only show objects that have been visible before
		for i in list(self.visible):
			self.objects[i].Show()
		
			
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
		
		
	def Hide(self):
		"""
		Hide the whole object,
		but remember which fits were visible
		"""
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
		


class FitInterface:
	"""
	User interface for fitting 1-d spectra
	"""
	def __init__(self, window, spectra):
		print "Loaded user interface for fitting of 1-d spectra"
		self.window = window
		self.spectra = spectra

		self.peakModel = "theuerkauf"
		self.bgdeg = 1 
		self.activeFit = Fit(Fitter(self.peakModel, self.bgdeg))
		self.activeFit.Draw(self.window.viewport)


		# tv commands
		self.tv = TvFitInterface(self)

		# Register hotkeys
		self.window.AddHotkey(ROOT.kKey_b, self._PutBgMarker)
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
			self.window.viewport.SetStatusText("No active spectrum")
			return
		try:
			self.spectra[self.spectra.activeID].ShowPrev()
		except AttributeError:
			self.window.viewport.SetStatusText("No fits available")
			
			
	def _HotkeyShowNext(self):
		"""
		ShowNext wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.viewport.SetStatusText("No active spectrum")
			return
		try:
			self.spectra[self.spectra.activeID].ShowNext()
		except AttributeError:
			self.window.viewport.SetStatusText("No fits available")
			
			
	def _HotkeyShow(self, arg):
		"""
		Show wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.viewport.SetStatusText("No active spectrum")
			return
		try:
			ids = [int(a) for a in arg.split()]
			self.spectra[self.spectra.activeID].ShowObjects(ids)		
		except ValueError:
			self.window.viewport.SetStatusText("Invalid fit identifier: %s" % arg)

	def _HotkeyActivate(self, arg):
		"""
		ActivateObject wrapper for use with a Hotkey (internal use)
		"""
		if self.spectra.activeID==None:
			self.window.viewport.SetStatusText("No active spectrum")
			return
		try:
			ID = int(arg)
			self.ActivateFit(ID)
		except ValueError:
			self.window.viewport.SetStatusText("Invalid fit identifier: %s" % arg)
		except KeyError:
			self.window.viewport.SetStatusText("No such id: %d" % ID)


	def _PutRegionMarker(self):
		fit = self.GetActiveFit()
		fit.PutRegionMarker(self.window.viewport.GetCursorX())
		
	def _PutPeakMarker(self):
		fit = self.GetActiveFit()
		fit.PutPeakMarker(self.window.viewport.GetCursorX())

	def _PutBgMarker(self):
		fit = self.GetActiveFit()
		fit.PutBgMarker(self.window.viewport.GetCursorX())


	def GetActiveFit(self):
		if not self.spectra.activeID==None:
			spec = self.spectra[self.spectra.activeID]
			if hasattr(spec, "activeID") and not spec.activeID==None:
				return spec[spec.activeID]
		return self.activeFit


	def FitBackground(self):
		"""
		Fit the background
		
		This only fits the background with a polynom of self.bgDegree
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if not hasattr(spec, "activeID"):
			# create SpectrumCompound object 
			spec = SpectrumCompound(self.window.viewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
			self.spectra[self.spectra.activeID]=spec
		if spec.activeID==None:
			ID = spec.GetFreeID()
			spec[ID]=self.activeFit
			spec.ActivateObject(ID)
			# fresh Fit
			self.activeFit = Fit(Fitter(self.peakModel, self.bgdeg)) 
			self.activeFit.Draw(self.window.viewport)
		fit = spec[spec.activeID]
		fit.FitBgFunc(spec)
		fit.Draw(self.window.viewport)
		

	def FitPeaks(self):
		"""
		Fit the peak
		
		If there are background markers, a background fit it included.
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if not hasattr(spec, "activeID"):
			# create SpectrumCompound object 
			spec = SpectrumCompound(self.window.viewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
			self.spectra[self.spectra.activeID]=spec
		if spec.activeID==None:
			ID = spec.GetFreeID()
			spec[ID]=self.activeFit
			spec.ActivateObject(ID)
			# fresh Fit
			self.activeFit = Fit(Fitter(self.peakModel, self.bgdeg)) 
			self.activeFit.Draw(self.window.viewport)
		fit = spec[spec.activeID]
		if len(fit.bgMarkers)>0:
			fit.FitBgFunc(spec)
		fit.FitPeakFunc(spec)
		fit.Draw(self.window.viewport)


	def ActivateFit(self, ID):
		"""
		Activate one fit
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if not hasattr(spec, "activeID"):
			print 'There are no fits for this spectrum'
			return
		if not spec.activeID==None:
			# keep current status of old fit
			self.KeepFit()
		# activate another fit
		spec.ActivateObject(ID)
		spec[spec.activeID].Show()
		
	
	def KeepFit(self):
		"""
		Keep this fit, 
		"""
		# get active spectrum
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		spec = self.spectra[self.spectra.activeID]
		if not hasattr(spec, "activeID") or spec.activeID==None:
			# do the fit
			self.FitPeaks()
		# FIXME: we need SetColor for markers!
		spec[spec.activeID].SetColor(spec.color)
		# remove the fit, if it is empty (=nothing fitted)
		if len(spec[spec.activeID].dispFuncs)==0:
			spec.pop(spec.activeID)
		# deactivate all objects
		spec.ActivateObject(None)


	def ClearFit(self):
		"""
		Clear all fit markers and the pending fit, if there is one
		"""
		fit = self.GetActiveFit()
		fit.Remove()

	
	def ClearBackground(self):
		"""
		Clear Background markers and refresh fit without background
		"""
		fit  = self.GetActiveFit()
		# remove background markers
		while len(fit.bgMarkers)>0:
			fit.bgMarkers.pop().Remove()
		# redo Fit without Background
			fit.Refresh()
		
	def SetDecomp(self, stat=True):
		"""
		Show peak decomposition
		"""
		fit = self.GetActiveFit()
		fit.SetDecomp(stat)
		

	def SetBgDeg(self, bgdeg):
		self.bgdeg = bgdeg
		fit = self.GetActiveFit()
		fit.fitter.bgdeg = bgdeg
		fit.Refresh()
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()


	def ShowFitStatus(self):
		fitter = self.GetActiveFit().fitter
		statstr = str()
		statstr += "Background model: polynomial, deg=%d\n" % fitter.bgdeg
		statstr += "Peak model: %s\n" % fitter.Name()
		statstr += "\n"
		statstr += fitter.OptionsStr()
		print statstr

# TODO: Testing!
	def SetFitParameters(self, parname, status):
		fit = self.GetActiveFit()
		fit.fitter.SetParameter(parname, status)
		fit.Refresh()
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()


# TODO: Testing!
	def ResetFitParameters(self, parname):
		fit = self.GetActiveFit()
		fit.fitter.ResetParameter(parname)
		fit.Refresh()
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()


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
		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)

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
		self.fitIf.ShowFitStatus()

	def FitParamReset(self, args):
		self.fitIf.ResetFitParameters()
	

# FIXME!
#	def FitParam(self, param, args):
#		try:
#			self.fitIf.SetFitParameters(param, " ".join(args))
#		except ValueError:
#			print "Usage: fit parameter <parname> [free|ifree|hold|disable|<number>]"
#			return False
#		except RuntimeError, e:
#			print e
#			return False

#	def PeakModelCompleter(self, text):
#		return hdtv.util.GetCompleteOptions(text, hdtv.fitter.gPeakModels.iterkeys())
#			
#	def SetPeakModel(self, args):
#		"""
#		Set the peak model (function used for fitting peaks)
#		"""
#		


#		# Unregister old parameters
#		for param in fitter.OrderedParamKeys():
#			hdtv.cmdline.RemoveCommand("fit param %s" % param)

#		# Set new peak model
#		fitter.SetPeakModel(args[0].lower())
#		
#		# Register new parameters
#		def MakeParamCmd(param):
#			return lambda args: self.FitParam(param, args)

#		for param in fitter.OrderedParamKeys():
#			hdtv.cmdline.AddCommand("fit param %s" % param,
#			                        MakeParamCmd(param),
#			                        minargs=1)
		
		# Update options
		self.fFitGui.FitUpdateOptions()
		self.fFitGui.FitUpdateData()





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
		



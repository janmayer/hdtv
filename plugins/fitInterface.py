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
import hdtv.fitio

from hdtv.spectrum import SpectrumCompound
from hdtv.marker import MarkerCollection
from hdtv.fitter import Fitter
from hdtv.fit import Fit
from hdtv.fitpanel import FitPanel

class FitInterface:
	"""
	User interface for fitting 1-d spectra
	"""
	def __init__(self, window, spectra, show_panel=True):
		print "Loaded user interface for fitting of 1-d spectra"
		self.window = window
		self.spectra = spectra

		self.defaultFitter = Fitter(peakModel="theuerkauf",bgdeg=1)
		self.activeFit = Fit(self.defaultFitter.Copy())
		self.activeFit.Draw(self.window.viewport)

		# tv commands
		self.tv = TvFitInterface(self)

		# fit panel
		self.fitPanel = FitPanel()
		self.fitPanel.fFitHandler = self.FitPeaks
		self.fitPanel.fClearHandler = self.ClearFit
		self.fitPanel.fResetHandler = self.ResetParameters
		self.fitPanel.fDecompHandler = lambda(stat): self.SetDecomp(stat)
		if show_panel:
			self.fitPanel.Show()

		# Register hotkeys
		self.window.AddHotkey(ROOT.kKey_b, self._PutBgMarker)
		self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_b], self._DeleteBgMarker)
		self.window.AddHotkey(ROOT.kKey_r, self._PutRegionMarker)
		self.window.AddHotkey(ROOT.kKey_p, self._PutPeakMarker)
		self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_p], self._DeletePeakMarker)
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
		"""
		Put region marker to the current position of cursor (internal use)
		"""
		fit = self.GetActiveFit()
		fit.PutRegionMarker(self.window.viewport.GetCursorX())
		

	def _PutPeakMarker(self):
		"""
		Put peak marker to the current position of cursor (internal use)
		"""
		fit = self.GetActiveFit()
		fit.PutPeakMarker(self.window.viewport.GetCursorX())

	def _PutBgMarker(self):
		"""
		Put background marker to the current position of cursor (internal use)
		"""
		fit = self.GetActiveFit()
		fit.PutBgMarker(self.window.viewport.GetCursorX())


	def _DeleteBgMarker(self):
		"""
		Delete the background marker that is nearest to cursor (internal use)
		"""
		fit = self.GetActiveFit()
		fit.bgMarkers.RemoveNearest(self.window.viewport.GetCursorX())


	def _DeletePeakMarker(self):
		"""
		Delete the peak marker that is nearest to cursor (internal use)
		"""
		fit = self.GetActiveFit()
		fit.peakMarkers.RemoveNearest(self.window.viewport.GetCursorX())


	def GetActiveFit(self):
		"""
		Returns the currently active fit
		"""
		if not self.spectra.activeID==None:
			spec = self.spectra[self.spectra.activeID]
			if hasattr(spec, "activeID") and not spec.activeID==None:
				return spec[spec.activeID]
		if not self.activeFit:
			self.activeFit = Fit(self.defaultFitter.Copy())
			self.activeFit.Draw(self.window.viewport)
		return self.activeFit
		
	
	def FitBackground(self):
		"""
		Fit the background
		
		This only fits the background with a polynom of self.bgDegree
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		if self.fitPanel:
			self.fitPanel.Show()
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
			self.activeFit = None
		fit = spec[spec.activeID]
		fit.FitBgFunc(spec)
		fit.Draw(self.window.viewport)
		self.UpdateFitPanel()


	def FitPeaks(self):
		"""
		Fit the peak
		
		If there are background markers, a background fit it included.
		"""
		if self.spectra.activeID==None:
			print "There is no active spectrum"
			return 
		if self.fitPanel:
			self.fitPanel.Show()
		spec = self.spectra[self.spectra.activeID]
		if not hasattr(spec, "activeID"):
			# create SpectrumCompound object 
			spec = SpectrumCompound(self.window.viewport, spec)
			# replace the simple spectrum object by the SpectrumCompound
			self.spectra[self.spectra.activeID]=spec
		if spec.activeID==None:
			ID = spec.GetFreeID()
			spec[ID]=self.activeFit
			self.activeFit = None
			spec.ActivateObject(ID)
		fit = spec[spec.activeID]
		if len(fit.bgMarkers)>0:
			fit.FitBgFunc(spec)
		fit.FitPeakFunc(spec)
		fit.Draw(self.window.viewport)
		# update fitPanel
		self.UpdateFitPanel()


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
		if not self.spectra.activeID in self.spectra.visible:
			print 'Warning: active spectrum (id=%s) is not visible' %self.spectra.activeID
		if not spec.activeID==None:
			# keep current status of old fit
			self.KeepFit()
		elif self.activeFit:
			self.activeFit.Remove()
			self.activeFit = None
		# activate another fit
		spec.ActivateObject(ID)
		if self.spectra.activeID in self.spectra.visible:
			spec[spec.activeID].Show()
		# update fitPanel
		self.UpdateFitPanel()

	
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
		# update fitPanel
		self.UpdateFitPanel()

	
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
		# update fitPanel
		self.UpdateFitPanel()
		
	
	def FitMultiSpectra(self, ids):
		self.window.viewport.LockUpdate()
		# save the current fit as template for the other fits
		fit = self.GetActiveFit().Copy(cal=None)
		if not self.spectra.activeID==None:
			spec = self.spectra[self.spectra.activeID]
			if hasattr(spec, "activeID") and not spec.activeID==None:
				ID = spec.activeID
				# deactivate fit
				spec.ActivateObject(None)
				# and delete from spectrum
				spec.pop(ID)
		if self.activeFit:
			self.activeFit.Remove()
		for ID in ids:
			try:
				spec = self.spectra[ID]
			except KeyError:
				print "Warning: ID %s not found" % ID
				continue
			try:
				# deactive all objects
				spec.ActiveObject(None)
			except AttributeError:
				# create SpectrumCompound object 
				spec = SpectrumCompound(self.window.viewport, spec)
				# replace the simple spectrum object by the SpectrumCompound
				self.spectra[ID]=spec
			fitID = spec.GetFreeID()
			spec[fitID] = fit.Copy(cal=spec.cal, color=spec.color)
			if len(spec[fitID].bgMarkers)>0:
				spec[fitID].FitBgFunc(spec)
			spec[fitID].FitPeakFunc(spec)
			spec[fitID].Draw(self.window.viewport)
			if not ID==self.spectra.activeID:
				spec[fitID].Hide()
		self.window.viewport.UnlockUpdate()
			


	def SetDecomp(self, stat=True):
		"""
		Show peak decomposition
		"""
		fit = self.GetActiveFit()
		fit.SetDecomp(stat)
		if self.fitPanel:
			self.fitPanel.SetDecomp(stat)
		

	def SetBgDeg(self, bgdeg):
		# change default fitter
		self.defaultFitter.bgdeg = bgdeg
		# and for active fit
		fit = self.GetActiveFit()
		fit.fitter.bgdeg = bgdeg
		fit.Refresh()
		# Update fitPanel
		self.UpdateFitPanel()


	def ShowFitStatus(self):
		fitter = self.GetActiveFit().fitter
		statstr = str()
		statstr += "Background model: polynomial, deg=%d\n" % fitter.bgdeg
		statstr += "Peak model: %s\n" % fitter.Name()
		statstr += "\n"
		statstr += fitter.OptionsStr()
		print statstr


	def SetParameter(self, parname, status):
		# change default fitter
		self.defaultFitter.SetParameter(parname, status)
		# and active fit
		fit = self.GetActiveFit()
		fit.fitter.SetParameter(parname, status)
		fit.Refresh()
		# Update fitPanel
		self.UpdateFitPanel()


	def ResetParameters(self):
		# change default fitter
		self.defaultFitter.ResetParamStatus()
		# and active fit
		fit = self.GetActiveFit()
		fit.fitter.ResetParamStatus()
		fit.Refresh()
		# Update fitPanel
		self.UpdateFitPanel()


	def SetPeakModel(self, peakmodel):
		"""
		Set the peak model (function used for fitting peaks)
		"""
		fit = self.GetActiveFit()
		fitter = fit.fitter
		if self.tv:
			# Unregister old parameter
			self.tv.UnregisterFitParameter(fitter)
		# Set new peak model
		self.defaultFitter.SetPeakModel(peakmodel)
		fitter.SetPeakModel(peakmodel)
		if self.tv:
			# Register new parameter
			self.tv.RegisterFitParameter(fitter)
		fit.Refresh()
		# Update fit panel
		self.UpdateFitPanel()
			

	def UpdateFitPanel(self):
		if not self.fitPanel:
			return
		fitter = self.GetActiveFit().fitter
		# options
		text = str()
		text += "Background model: polynomial, deg=%d\n" % fitter.bgdeg
		text += "Peak model: %s\n" % fitter.peakModel.Name()
		text += "\n"
		text += fitter.peakModel.OptionsStr()
		self.fitPanel.SetOptions(text)
		# data
		text = str()
		if fitter.bgFitter:
			deg = fitter.bgFitter.GetDegree()
			chisquare = fitter.bgFitter.GetChisquare()
			text += "Background (seperate fit): degree = %d   chi^2 = %.2f\n" % (deg, chisquare)
			for i in range(0,deg+1):
				value = hdtv.util.ErrValue(fitter.bgFitter.GetCoeff(i),
				                           fitter.bgFitter.GetCoeffError(i))
				text += "bg[%d]: %s   " % (i, value.fmt())
			text += "\n\n"
		i = 1
		if fitter.peakFitter:
			text += "Peak fit: chi^2 = %.2f\n" % fitter.peakFitter.GetChisquare()
			for peak in fitter.resultPeaks:
				text += "Peak %d:\n%s\n" % (i, str(peak))
				i += 1
		self.fitPanel.SetData(text)
		

class TvFitInterface:
	"""
	TV style interface for fitting
	"""
	def __init__(self, fitInterface):
		self.fitIf = fitInterface
		self.spectra = self.fitIf.spectra


		# register tv commands
		self.RegisterFitParameter(self.fitIf.defaultFitter)
		
		hdtv.cmdline.AddCommand("fit list", self.FitList, nargs=0, usage="fit list")
		hdtv.cmdline.AddCommand("fit write", self.FitWrite, nargs=0,
		                        usage="fit write <filename>")
		hdtv.cmdline.AddCommand("fit show", self.FitShow, minargs=1)
		hdtv.cmdline.AddCommand("fit delete", self.FitDelete, minargs=1)
		hdtv.cmdline.AddCommand("fit activate", self.FitActivate, nargs=1)
		hdtv.cmdline.AddCommand("fit multi", self.FitMulti, minargs=1)
		hdtv.cmdline.AddCommand("fit param background degree", self.FitParamBgDeg, nargs=1)
		hdtv.cmdline.AddCommand("fit param status", self.FitParamStatus, nargs=0)
		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)
		hdtv.cmdline.AddCommand("fit function peak activate", self.FitSetPeakModel,
								completer=self.PeakModelCompleter, nargs=1)
		
		hdtv.cmdline.AddCommand("calibration position assign", self.CalPosAssign, minargs=2)
	
	
	def RegisterFitParameter(self, fitter):
		# we need to create the function outside the loop
		def MakeSetFunction(param):
			return lambda args: self.fitIf.SetParameter(param," ".join(args))
		# create new commands 
		for param in fitter.OrderedParamKeys():
			hdtv.cmdline.AddCommand("fit param %s" % param, MakeSetFunction(param), minargs=1)

	def UnregisterFitParameter(self, fitter):
		# Unregister old parameters
		for param in fitter.OrderedParamKeys():
			hdtv.cmdline.RemoveCommand("fit param %s" % param)


	def FitWrite(self, args):
		"""
		Write a list of all fits belonging to the active spectrum to an XML file
		"""
		try:
			spec = self.spectra[self.spectra.activeID]
			if self.spectra.activeID in self.spectra.visible:
				visible = True
			else:
				visible = False
		except KeyError:
			print "No active spectrum"
			return False
		except AttributeError:
			print "There are no fits for this spectrum"
			return False
		except:
			return "USAGE"
			
		print 'Dumping fits belonging to %s (visible=%s):' %(str(spec), visible)
		hdtv.fitio.FitIO().Write(spec)


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
			return "USAGE"
		
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
			print "Usage: spectrum delete <ids>|all"
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
			print "Usage: fit show <ids>|all|none"
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


	def FitMulti(self, args):
		try:
			ids = hdtv.cmdhelper.ParseRange(args, ["all", "shown"])
		except ValueError:
			print "Usage: fit fit <ids>|all|shown"
			return False
		if ids == "ALL":
			ids = self.spectra.keys()
		elif ids =="SHOWN":
			ids = list(self.spectra.visible)
		self.fitIf.FitMultiSpectra(ids)


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
		self.fitIf.ResetParameters()
	
	def FitSetPeakModel(self, args):
		self.fitIf.SetPeakModel(args[0].lower())


	def PeakModelCompleter(self, text):
		return hdtv.util.GetCompleteOptions(text, hdtv.fitter.gPeakModels.iterkeys())
			


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
		

# plugin initialisation
import __main__
if not hasattr(__main__,"window"):
	import hdtv.window
	__main__.window = hdtv.window.Window()
if not hasattr(__main__, "spectra"):
	import hdtv.drawable
	__main__.spectra = hdtv.drawable.DrawableCompound(__main__.window.viewport)
__main__.f = FitInterface(__main__.window, __main__.spectra, show_panel=False)



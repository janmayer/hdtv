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
		
	def __getattr__(self, name):
		"""
		Dispatch everything which is unknown to this object to the spectrum
		"""
		return getattr(self.spec, name)

	def Refresh(self):
		self.spec.Refresh()
		DrawableCompound.Refresh(self)
		
	def Draw(self, viewport):
		self.spec.Draw(viewport)
		DrawableCompound.Draw(self, viewport)
		
	def Show(self):
		self.spec.Show()
		DrawableCompound.Show(self)
		
	def Hide(self):
		self.spec.Hide()
		DrawableCompound.Hide(self)


class TVFitInterface():
	"""
	
	"""
	def __init__(self, window, spectra):
		print "Loaded commands for 1-d histograms fitting"
		self.window = window
		self.spectra = spectra
		self.peakModel= "theuerkauf"
		self.bgDegree = 1
		self.activePeakMarkers = []
		self.activeRegionMarkers = []
		self.activeBgMarkers = []

	

		# Register hotkeys
		self.window.AddHotkey(ROOT.kKey_b, self.PutBackgroundMarker)
		self.window.AddHotkey(ROOT.kKey_r, self.PutRegionMarker)
		self.window.AddHotkey(ROOT.kKey_p, self.PutPeakMarker)
		self.window.AddHotkey(ROOT.kKey_B, self.FitBackground)
	  	self.window.AddHotkey(ROOT.kKey_F, self.FitPeaks)
#	  	self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_F], self.DeleteFit)
#	  	self.window.AddHotkey(ROOT.kKey_I, self.Integrate)
	  	self.window.AddHotkey(ROOT.kKey_D, lambda: self.SetDecomp(True))
	  	self.window.AddHotkey([ROOT.kKey_Minus, ROOT.kKey_D], lambda: self.SetDecomp(False))
	
#		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_p], ?.ShowPrev)
#		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_n], ?.ShowNext)
#		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_s],
#		        lambda: self.window.EnterEditMode(prompt="Show Fit: ",
#		                                   handler=self.HotkeyShow))
#		self.window.AddHotkey([ROOT.kKey_f, ROOT.kKey_a],
#		        lambda: self.window.EnterEditMode(prompt="Activate Fit: ",
#		                                   handler=self.HotkeyActivate))


		# register tv commands
#		hdtv.cmdline.AddCommand("fit param background degree", self.FitParamBgDeg, nargs=1)
#		hdtv.cmdline.AddCommand("fit param status", self.FitParamStatus, nargs=0)
#		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)


	def PutRegionMarker(self):
		"Put a region marker at the current cursor position (internal use only)"
		self.window.PutPairedMarker("X", "REGION", self.activeRegionMarkers, 1)
			
	def PutBackgroundMarker(self):
		"Put a background marker at the current cursor position (internal use only)"
		self.window.PutPairedMarker("X", "BACKGROUND", self.activeBgMarkers)
		
	def PutPeakMarker(self):
		"Put a peak marker at the current cursor position (internal use only)"
		pos = self.window.fViewport.GetCursorX()
  		self.activePeakMarkers.append(Marker("PEAK", pos))
  		self.activePeakMarkers[-1].Draw(self.window.fViewport)

	def FitBackground(self):
		fit = self.GetActiveFit()
		fit.DrawBgFunc(self.window.fViewport)
		
	
	def FitPeaks(self):
		fit = self.GetActiveFit()
		fit.Draw(self.window.fViewport)
		
	
	def GetActiveFit(self):
		spec = self.spectra.GetActiveObject()
		if not spec:
			print "There is no active spectrum"
			return
		try:
			fit = spec.GetActiveObject()
		except AttributeError:
			print spec
			spec = SpectrumCompound(self.window.fViewport, spec)
			self.spectra[self.spectra.activeID]=spec
			fit = None
		if fit:
			# update 
			fit.regionMarkers = self.activeRegionMarkers
			fit.peakMarkers = self.activePeakMarkers
			fit.bgMarkers = self.activeBgMarkers
			fit.fitter.SetPeakModel(self.peakModel)
			fit.fitter.bgdeg = self.bgDegree
		else:
			# create new
			fitter = Fitter(spec.spec, self.peakModel, self.bgDegree)
			fit = Fit(fitter, self.activeRegionMarkers, self.activePeakMarkers, 
							  self.activeBgMarkers, color=spec.color)
			spec.Add(fit)
		return fit

	def SetDecomp(self, stat):
		pass

		
		










		
#		def MakePeakModelCmd(name):
#			return lambda args: self.FitSetPeakModel(name)
#		for name in hdtv.fit.gPeakModels.iterkeys():
#			hdtv.cmdline.AddCommand("fit function peak activate %s" % name,
#			                        MakePeakModelCmd(name), nargs=0)


#	def FitParamBgDeg(self, args):
#		try:
#			bgdeg = int(args[0])
#		except ValueError:
#			print "Usage: fit parameter background degree <deg>"
#			return False
#			
#		self.fFitGui.fFitter.bgdeg = bgdeg

#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()
#		
#	def FitParamStatus(self, args):
#		self.fFitGui.fFitter.PrintParamStatus()
#		
#	def FitParamPeak(self, parname, args):
#		try:
#			self.fFitGui.fFitter.SetParameter(parname, " ".join(args))
#		except ValueError:
#			print "Usage: fit parameter <parname> [free|ifree|hold|disable|<number>]"
#			return False
#		except RuntimeError, e:
#			print e
#			return False
#			
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()
#		
#	def FitParamReset(self, args):
#		self.fFitGui.ResetFitParameters()
#			
#	def FitSetPeakModel(self, name):
#		# Unregister old parameters
#		for param in self.fFitGui.fFitter.GetParameters():
#			hdtv.cmdline.RemoveCommand("fit param %s" % param)
#		
#		# Set new peak model
#		self.fFitGui.fFitter.SetPeakModel(name.lower())
#		
#		# Register new parameters
#		def MakeParamCmd(param):
#			return lambda args: self.FitParamPeak(param, args)
#		for param in self.fFitGui.fFitter.GetParameters():
#			hdtv.cmdline.AddCommand("fit param %s" % param, 
#			                        MakeParamCmd(param),
#			                        minargs=1)
#			                        
#		# Update options
#		self.fFitGui.FitUpdateOptions()
#		self.fFitGui.FitUpdateData()


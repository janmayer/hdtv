import ROOT
import os
import glob

import hdtv.cmdline
import hdtv.cmdhelper
from hdtv.window import Window
from hdtv.manager import ObjectManager
from hdtv.spectrum import Spectrum, FileSpectrum
from hdtv.fitgui import FitGUI

# Don't add created spectra to the ROOT directory
ROOT.TH1.AddDirectory(ROOT.kFALSE)

class TVSpecInterface(ObjectManager):
	"""
	This class tries to model an interface to hdtv that is a close to the good 
	old tv as possible. 
	"""
	def __init__(self):
		ObjectManager.__init__(self)
		self.fFitGui = FitGUI(self.fWindow, show_panel=True)
		self.FitSetPeakModel("theuerkauf")
		
		# register common tv hotkeys
		self.fWindow.AddHotkey([ROOT.kKey_N, ROOT.kKey_p], self.ShowPrev)
		self.fWindow.AddHotkey([ROOT.kKey_N, ROOT.kKey_n], self.ShowNext)
		self.fWindow.AddHotkey(ROOT.kKey_Greater, lambda: self.fWindow.fViewport.ShiftXOffset(0.1))
		self.fWindow.AddHotkey(ROOT.kKey_Less, lambda: self.fWindow.fViewport.ShiftXOffset(-0.1))
		self.fWindow.AddHotkey(ROOT.kKey_Equal, self.RefreshAll)
		self.fWindow.AddHotkey(ROOT.kKey_t, self.RefreshVisible)
		self.fWindow.AddHotkey(ROOT.kKey_Bar, self.CenterXOnCursor)
		
		# register tv commands
		hdtv.cmdline.command_tree.SetDefaultLevel(1)
		hdtv.cmdline.AddCommand("spectrum get", self.SpectrumGet, level=0, minargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("spectrum list", self.SpectrumList, nargs=0)
		hdtv.cmdline.AddCommand("spectrum delete", self.SpectrumDelete, minargs=1)
		hdtv.cmdline.AddCommand("spectrum activate", self.SpectrumActivate, nargs=1)
		hdtv.cmdline.AddCommand("spectrum show", self.SpectrumShow, minargs=1)
		hdtv.cmdline.AddCommand("spectrum update", self.SpectrumUpdate, minargs=1)
		hdtv.cmdline.AddCommand("spectrum write", self.SpectrumWrite, minargs=1, maxargs=2)
			
		hdtv.cmdline.AddCommand("cd", self.Cd, level=2, maxargs=1, dirargs=True)
		
		hdtv.cmdline.AddCommand("calibration position read", self.CalPosRead, nargs=1, fileargs=True)
		hdtv.cmdline.AddCommand("calibration position enter", self.CalPosEnter, nargs=4)
		hdtv.cmdline.AddCommand("calibration position set", self.CalPosSet, minargs=2)
		
		hdtv.cmdline.AddCommand("fit param background degree", self.FitParamBgDeg, nargs=1)
		hdtv.cmdline.AddCommand("fit param status", self.FitParamStatus, nargs=0)
		hdtv.cmdline.AddCommand("fit param reset", self.FitParamReset, nargs=0)
		
		def MakePeakModelCmd(name):
			return lambda args: self.FitSetPeakModel(name)
		for name in hdtv.fit.gPeakModels.iterkeys():
			hdtv.cmdline.AddCommand("fit function peak activate %s" % name,
			                        MakePeakModelCmd(name), nargs=0)
				
		hdtv.cmdline.RegisterInteractive("gSpectra", self.fWindow)
		
	
	def CenterXOnCursor(self):
		self.fWindow.fViewport.SetXCenter(self.fWindow.fViewport.GetCursorX())
		
	
	def LoadSpectrum(self, fname, fmt=None):
		"""
		Load a spectrum from file
		
		The spectrum is shown in an appropriate color.
		"""
		spec = FileSpectrum(fname, fmt)
		if spec == None:
			return None
		else:
			ID = self.GetFreeID()
			spec.SetColor(self.ColorForID(ID, 1., 1.))
			self[ID] = spec
			self.fFitGui.fFitter.spec = spec
			return ID


	def SpectrumGet(self, args):
		"""
		Load a list of spectra
		
		It is possible to use wildcards. 
		"""
		# Avoid multiple updates
		self.fWindow.fViewport.LockUpdate()
		if type(args) == str or type(args) == unicode:
			args = [args]
		nloaded = 0
		for arg in args:
			# PUT FMT IF AVAILABLE
			sparg = arg.rsplit("'", 1)
			if len(sparg) == 1 or not sparg[1]:
				(pat, fmt) = (sparg[0], None)
			else:
				(pat, fmt) = sparg
			path = os.path.expanduser(pat)
			for fname in glob.glob(path):
				if self.LoadSpectrum(fname, fmt) != None:
					nloaded += 1
		if nloaded == 0:
			print "Warning: no spectra loaded."
		elif nloaded == 1:
			print "Loaded 1 spectrum"
		else:
			print "Loaded %d spectra" % nloaded
		# Update viewport if required
		self.fWindow.fViewport.UnlockUpdate()

	
	def SpectrumList(self, args):
		"""
		Show all loaded spectra and their status
		"""
		self.ListObjects()
		
		
	def SpectrumDelete(self, args):
		""" 
		Deletes spectra 
		
		It is possible to use the keyword all to delete 
		all spectra that are currently loaded.
		"""
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			return
		elif ids == "ALL":
			ids = self.keys()
		self.DeleteObjects(ids)
		
		
	def SpectrumActivate(self, args):
		"""
		Activate one spectra
		
		There is only just one single spectrum activated.
		Actions that work only on one spectrum usually 
		work on the activated one.
		"""
		try:
			sid = int(args[0])
		except ValueError:
			print "Usage: spectrum activate <id>"
			return
		self.ActivateObject(sid)
		self.fFitGui.fFitter.spec = self[self.fActiveID]
		
		
	def SpectrumShow(self, args):
		"""
		Shows spectra
		
		One can use the keywords none or all here, 
		or give a list of id numbers with space a seperator
		"""
		ids = hdtv.cmdhelper.ParseRange(args)
		if ids == "NONE":
			self.HideAll()
		elif ids == "ALL":
			self.ShowAll()
		else:
			self.Show(ids)
			
	
	def SpectrumUpdate(self, args):
		ids = hdtv.cmdhelper.ParseRange(args, ["all", "shown"])
		if ids == "ALL":
			self.RefreshAll()
		elif ids == "SHOWN":
			self.RefreshVisible()
		else:
			self.Refresh(ids)
			
			
	def SpectrumWrite(self, args):
		"""
		Writes out a spectrum to file
		
		The user must define the file name and the file format.
		If no id is given this action works on the activated spectrum.
		"""
		try:
			(fname, fmt) = args[0].rsplit("'", 1)
			fname = os.path.expanduser(fname)
			if len(args) == 1:
				if self.fActiveID == None:
					print "Warning: No active spectrum, no action taken."
					return False
				self[self.fActiveID].WriteSpectrum(fname, fmt)
			else:
				sid = int(args[1])
				try:				
					self[sid].WriteSpectrum(fname, fmt)
				except KeyError:
					print "Error: ID %d not found" % sid
		except ValueError:
			print "Usage: spectrum write <filename>'<format> [index]"
		return

		
	def Cd(self, args):
		"""
		Change current working directory
		"""
		if len(args) == 0:
			print os.getcwdu()
		else:
			try:
				os.chdir(os.path.expanduser(args[0]))
			except OSError, msg:
				print msg


	def CalPosRead(self, args):
		"""
		Read calibration from file
		"""
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		self[self.fActiveID].ReadCal(args[0])

		
	def CalPosEnter(self, args):
		"""
		Create calibration from two pairs of channel and energy
		"""
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		try:
			p0 = [float(args[0]), float(args[1])]
			p1 = [float(args[2]), float(args[3])]
		except ValueError:
			print "Usage: calibration position enter <ch0> <E0> <ch1> <E1>"
			return False
		self[self.fActiveID].CalFromPairs([p0, p1])
	
	
	def CalPosSet(self, args):
		"""
		Create a calibration from the coefficients of a calibration polynom.
		
		Coefficients are ordered from lowest exponent to highes.
		"""
		if self.fActiveID == None:
			print "Warning: No active spectrum, no action taken."
			return False
		try:
			for arg in args:
				calpoly = map(lambda s: float(s), args)
		except ValueError:
			print "Usage: calibration position set <p0> <p1> <p2> ..."
			return False
		self[self.fActiveID].SetCal(calpoly)
		
		
	def FitParamBgDeg(self, args):
		try:
			bgdeg = int(args[0])
		except ValueError:
			print "Usage: fit parameter background degree <deg>"
			return False
			
		self.fFitGui.fFitter.bgdeg = bgdeg

		# Update options
		self.fFitGui.FitUpdateOptions()
		self.fFitGui.FitUpdateData()
		
	def FitParamStatus(self, args):
		self.fFitGui.fFitter.PrintParamStatus()
		
	def FitParamPeak(self, parname, args):
		try:
			self.fFitGui.fFitter.SetParameter(parname, " ".join(args))
		except ValueError:
			print "Usage: fit parameter <parname> [free|ifree|hold|disable|<number>]"
			return False
		except RuntimeError, e:
			print e
			return False
			
		# Update options
		self.fFitGui.FitUpdateOptions()
		self.fFitGui.FitUpdateData()
		
	def FitParamReset(self, args):
		self.fFitGui.ResetFitParameters()
			
	def FitSetPeakModel(self, name):
		# Unregister old parameters
		for param in self.fFitGui.fFitter.GetParameters():
			hdtv.cmdline.RemoveCommand("fit param %s" % param)
		
		# Set new peak model
		self.fFitGui.fFitter.SetPeakModel(name.lower())
		
		# Register new parameters
		def MakeParamCmd(param):
			return lambda args: self.FitParamPeak(param, args)
		for param in self.fFitGui.fFitter.GetParameters():
			hdtv.cmdline.AddCommand("fit param %s" % param, 
			                        MakeParamCmd(param),
			                        minargs=1)
			                        
		# Update options
		self.fFitGui.FitUpdateOptions()
		self.fFitGui.FitUpdateData()

plugin = TVSpecInterface()
print "Loaded plugin spectrum (commands for 1-d histograms)"

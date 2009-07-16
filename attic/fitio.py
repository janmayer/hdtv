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
import sys
from xml.dom.minidom import getDOMImplementation

class FitIO:
    def __init__(self):
        pass
        
    def WriteFit(self, fit, fitNode):
        fitNode.setAttribute(u"region1", str(fit.regionMarkers[0].p1))
        fitNode.setAttribute(u"region2", str(fit.regionMarkers[0].p2))
        
        bgNode = self.createElement(u"background")
        self.WriteBackground(fit, bgNode)
        fitNode.appendChild(bgNode)
        
    
    def WriteBackground(self, fit, bgNode):
        for bg in fit.bgMarkers:
            regionNode = self.createElement(u"region")
            regionNode.setAttribute(u"p1", str(bg.p1))
            regionNode.setAttribute(u"p2", str(bg.p2))
            bgNode.appendChild(regionNode)
            
    def WritePeak(self):
        pass


    def WriteSpec(self, spec, specNode):
        if spec.fHist:
            name = spec.fHist.GetName()
        else:
            name = "__unknown__"

        specNode.setAttribute("name", name)
        
        try:
            fits = spec.objects.itervalues()
        except AttributeError:
            fits = []
            
        for fit in fits:
            fitNode = self.createElement(u"fit")
            self.WriteFit(fit, fitNode)
            specNode.appendChild(fitNode)

    def Write(self, spec):
        xmlDoc = getDOMImplementation().createDocument(None, None, None)
        self.createElement = xmlDoc.createElement

        specNode = self.createElement(u"spectrum")
        self.WriteSpec(spec, specNode)
        xmlDoc.appendChild(specNode)
        
        xmlDoc.writexml(sys.stdout, indent="", addindent="\t", newl="\n")
        xmlDoc.unlink()
    

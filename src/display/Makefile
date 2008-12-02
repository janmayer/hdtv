# Makefile for HDTV::Display

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= GSDisplaySpec.cxx GSDisplayFunc.cxx GSDisplayObj.cxx GSViewport.cxx GSViewer.cxx Painter.cxx GSMarker.cxx GSXMarker.cxx GSYMarker.cxx GSCalibration.cxx View.cxx View2D.cxx MTViewer.cxx
EXPHEADERS= GSDisplaySpec.h GSDisplayFunc.h GSDisplayObj.h GSMarker.h GSXMarker.h GSYMarker.h GSCalibration.h  View2D.h GSViewport.h View.h MTViewer.h GSViewer.h
HEADERS= $(EXPHEADERS) Painter.h
OBJ= $(SOURCES:.cxx=.o)
DESTDIR = ../../lib
MODNAME= display

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o

rootdict-$(MODNAME).cxx:  Makefile $(EXPHEADERS) LinkDef.h
	$(ROOTCINT) -f rootdict-$(MODNAME).cxx -c $(EXPHEADERS) LinkDef.h

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

copy: $(DESTDIR)/$(MODNAME).so

$(DESTDIR)/$(MODNAME).so: $(MODNAME).so
	cp $(MODNAME).so $(DESTDIR)

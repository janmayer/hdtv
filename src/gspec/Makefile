# Makefile for gSpec
#

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= GSDisplaySpec.cxx GSDisplayFunc.cxx GSDisplayObj.cxx GSViewport.cxx GSViewer.cxx GSPainter.cxx GSMarker.cxx GSXMarker.cxx GSYMarker.cxx GSCalibration.cxx GSFitter.cxx GSEEFitter.cxx MTView.cxx MTViewer.cxx
EXPHEADERS= GSViewer.h GSViewport.h GSDisplaySpec.h GSDisplayFunc.h GSDisplayObj.h GSMarker.h GSXMarker.h GSYMarker.h GSCalibration.h GSFitter.h GSEEFitter.h MTView.h MTViewer.h
HEADERS= $(EXPHEADERS) GSPainter.h
OBJ= $(SOURCES:.cxx=.o)
DESTDIR = ../../lib

.PHONY: all build copy clean

all: build copy

build: gspec.so

gspec.so: $(OBJ) gsdict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o gspec.so $(OBJ) gsdict.o

gsdict.cxx:  Makefile $(EXPHEADERS)
	$(ROOTCINT) -f gsdict.cxx -c $(EXPHEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	rm -f gsdict.cxx gsdict.h gsdict.o
	rm -f *~
	rm -f $(OBJ)

copy: build
	cp gspec.so $(DESTDIR)

# Makefile for gSpec
#

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= GSSpectrum.cxx GSDisplaySpec.cxx GSViewport.cxx GSViewer.cxx GSSpecPainter.cxx GSMarker.cxx LC2Reader.cxx mfile-tiny.cxx
HEADERS= GSSpectrum.h GSDisplaySpec.h GSViewport.h GSViewer.h GSSpecPainter.h GSMarker.h LC2Reader.h mfile-tiny.h
OBJ= $(SOURCES:.cxx=.o)

.PHONY: build clean

build: gspec.so

clean:
	-/bin/rm -f dict.cxx dict.h
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

gspec.so: $(OBJ) dict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o gspec.so $(OBJ) dict.o

dict.cxx: GSViewer.h GSSpectrum.h LC2Reader.h Makefile
	$(ROOTCINT) -f dict.cxx -c GSViewer.h GSSpectrum.h GSViewport.h LC2Reader.h

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<


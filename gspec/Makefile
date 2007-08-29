# Makefile for gSpec
#

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= GSDisplaySpec.cxx GSDisplayFunc.cxx GSDisplayObj.cxx GSViewport.cxx GSViewer.cxx GSPainter.cxx GSMarker.cxx
EXPHEADERS= GSViewer.h GSViewport.h GSDisplaySpec.h GSDisplayFunc.h GSDisplayObj.h GSMarker.h
HEADERS= $(EXPHEADERS) GSPainter.h
OBJ= $(SOURCES:.cxx=.o)

.PHONY: build clean

build: gspec.so

clean:
	-/bin/rm -f gsdict.cxx gsdict.h gsdict.o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

gspec.so: $(OBJ) gsdict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o gspec.so $(OBJ) gsdict.o

gsdict.cxx:  Makefile $(EXPHEADERS)
	$(ROOTCINT) -f gsdict.cxx -c $(EXPHEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<


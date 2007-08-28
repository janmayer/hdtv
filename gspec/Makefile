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
	-/bin/rm -f dict.cxx dict.h
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

gspec.so: $(OBJ) dict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o gspec.so $(OBJ) dict.o

dict.cxx:  Makefile $(EXPHEADERS)
	$(ROOTCINT) -f dict.cxx -c $(EXPHEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<


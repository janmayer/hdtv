# Makefile for gSpec
#

CPP=g++
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= GSTextSpectrumReader.cxx GSSpectrum.cxx GSDisplaySpec.cxx GSViewport.cxx GSViewer.cxx GSSpecPainter.cxx GSMarker.cxx gspec.cxx
HEADERS= GSTextSpectrumReader.h GSSpectrum.h GSDisplaySpec.h GSViewport.h GSViewer.h GSSpecPainter.h GSMarker.h gspec.h
OBJ= $(SOURCES:.cxx=.o)

.PHONY: build clean

build: gspec

clean:
	-/bin/rm -f Dict.cxx Dict.h
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

gspec: $(OBJ) Makefile
	$(CPP) $(LFLAGS) -o gspec $(OBJ)

Dict.cxx: gspec.h LinkDef.h Makefile
	$(ROOTCINT) -f Dict.cxx -c gspec.h LinkDef.h

Dict.o: Dict.cxx Makefile
	$(CPP) $(CFLAGS) -c $<

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -c $<

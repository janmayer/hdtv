# Makefile for HDTV::Display

CPP=g++
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags) -g -Wall
LFLAGS=$(shell root-config --glibs)
SOURCES= DisplaySpec.cxx DisplayFunc.cxx DisplayBlock.cxx DisplayObj.cxx DisplayStack.cxx Viewer.cxx Painter.cxx Marker.cxx XMarker.cxx YMarker.cxx Calibration.cxx View.cxx View1D.cxx View2D.cxx MTViewer.cxx
# The ordering matters here: rootcint will complain on (some) different orderings.
# The reason for this is unclear.
EXPHEADERS= Calibration.h View.h View1D.h View2D.h MTViewer.h Viewer.h DisplaySpec.h DisplayFunc.h DisplayBlock.h DisplayObj.h Marker.h XMarker.h YMarker.h
HEADERS= $(EXPHEADERS) Painter.h
OBJ= $(SOURCES:.cxx=.o)
DESTDIR = ../../hdtv/lib
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

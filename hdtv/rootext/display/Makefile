# Makefile for HDTV::Display
MODNAME = display

SOURCES= DisplaySpec.cxx DisplayFunc.cxx DisplayBlock.cxx DisplayObj.cxx DisplayStack.cxx DisplayCut.cxx Viewer.cxx Painter.cxx Marker.cxx XMarker.cxx YMarker.cxx Calibration.cxx View.cxx View1D.cxx View2D.cxx MTViewer.cxx
HEADERS= Calibration.h View.h View1D.h View2D.h MTViewer.h Viewer.h DisplaySpec.h DisplayFunc.h DisplayBlock.h DisplayObj.h DisplayCut.h Marker.h XMarker.h YMarker.h Painter.h
OBJ= $(SOURCES:.cxx=.o)

CPP = g++
ROOTCLING = rootcling
CFLAGS += $(shell root-config --cflags) -Wall -g -O2 -fPIC
LFLAGS += $(shell root-config --glibs)

.PHONY: all build clean

all: build

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o
	$(CPP) $(CFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o $(LFLAGS)

rootdict-$(MODNAME).cxx: $(HEADERS) LinkDef.h
	$(ROOTCLING) -f rootdict-$(MODNAME).cxx -inlineInputHeader $(HEADERS) LinkDef.h

%.o: %.cxx $(HEADERS)
	$(CPP) $(CFLAGS) -c -o $@ $<

%.o: %.c $(HEADERS)
	$(CPP) $(CFLAGS) -c -o $@ $<

clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o rootdict-$(MODNAME)_rdict.pcm
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)
	-/bin/rm -f *.so

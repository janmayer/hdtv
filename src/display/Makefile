# Makefile for HDTV::Display
include ../Makefile.def

SOURCES= DisplaySpec.cxx DisplayFunc.cxx DisplayBlock.cxx DisplayObj.cxx DisplayStack.cxx DisplayCut.cxx Viewer.cxx Painter.cxx Marker.cxx XMarker.cxx YMarker.cxx Calibration.cxx View.cxx View1D.cxx View2D.cxx MTViewer.cxx
# The ordering matters here: rootcint will complain on (some) different orderings.
# The reason for this is unclear.
EXPHEADERS= Calibration.h View.h View1D.h View2D.h MTViewer.h Viewer.h DisplaySpec.h DisplayFunc.h DisplayBlock.h DisplayObj.h DisplayCut.h Marker.h XMarker.h YMarker.h
HEADERS= $(EXPHEADERS) Painter.h
OBJ= $(SOURCES:.cxx=.o)
MODNAME= display

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o $(LFLAGS) 

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
	mkdir -p $(DESTDIR)
	cp $(MODNAME).so $(DESTDIR)

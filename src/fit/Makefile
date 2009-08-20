# Makefile for HDTV::Fit
include ../Makefile.def

# -Wwrite-strings causes a number of warnings that cannot be fixed with ROOT 5.18
CPP=g++ -g -Wall -Wno-write-strings
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= Integral.cxx PolyBg.cxx Param.cxx Fitter.cxx TheuerkaufFitter.cxx EEFitter.cxx Util.cxx
EXPHEADERS= Integral.h Background.h PolyBg.h Param.h Fitter.h TheuerkaufFitter.h EEFitter.h
HEADERS= $(EXPHEADERS)
OBJ= $(SOURCES:.cxx=.o)
MODNAME= fit

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

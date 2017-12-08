# Makefile for HDTV::Fit
MODNAME = fit

SOURCES= Integral.cxx PolyBg.cxx Param.cxx Fitter.cxx TheuerkaufFitter.cxx EEFitter.cxx Util.cxx
HEADERS= Integral.h Background.h PolyBg.h Param.h Fitter.h TheuerkaufFitter.h EEFitter.h Util.h
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

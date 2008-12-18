# Makefile for HDTV::Fit

CPP=g++ -g -Wall
CC=gcc -g -Wall
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= PolyBg.cxx Param.cxx TheuerkaufFitter.cxx EEFitter.cxx
EXPHEADERS= PolyBg.h Param.h TheuerkaufFitter.h EEFitter.h
HEADERS= $(EXPHEADERS)
OBJ= $(SOURCES:.cxx=.o)
DESTDIR= ../../lib
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

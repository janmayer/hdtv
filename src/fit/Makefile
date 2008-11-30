# Makefile for HDTV::Fit

CPP=g++ -g
CC=gcc -g
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= PolyBg.cxx Param.cxx TheuerkaufFitter.cxx EEFitter.cxx
EXPHEADERS= PolyBg.h Param.h TheuerkaufFitter.h EEFitter.h
HEADERS= $(EXPHEADERS)
OBJ= $(SOURCES:.cxx=.o)
DESTDIR= ../../lib
MODNAME= fit.so

.PHONY: all build copy clean

all: build copy

build: $(MODNAME)

$(MODNAME): $(OBJ) rootdict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o $(MODNAME) $(OBJ) rootdict.o

rootdict.cxx:  Makefile $(EXPHEADERS) LinkDef.h
	$(ROOTCINT) -f rootdict.cxx -c $(EXPHEADERS) LinkDef.h

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	rm -f rootdict.cxx rootdict.h rootdict.o
	rm -f *~
	rm -f $(OBJ)

copy: build
	cp $(MODNAME) $(DESTDIR)

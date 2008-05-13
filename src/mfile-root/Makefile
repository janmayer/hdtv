# Makefile for 
#

CPP=g++
CC=gcc
ROOTCINT=rootcint
INCL_PATH=-I/ikpv2/include
CFLAGS=$(shell root-config --cflags) $(INCL_PATH)
LFLAGS=$(shell root-config --glibs) -L/ikpv2/lib -lmfile
SOURCES= MFileHist.cxx VMatrix.cxx
HEADERS= MFileHist.h VMatrix.h
OBJ= $(SOURCES:.cxx=.o)
DESTDIR= ../../lib

.PHONY: all build copy clean

all: build copy

build: mfile-root.so

clean:
	-/bin/rm -f mfdict.cxx mfdict.h mfdict.o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

mfile-root.so: $(OBJ) mfdict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o mfile-root.so $(OBJ) mfdict.o

mfdict.cxx:  Makefile $(HEADERS)
	$(ROOTCINT) -f mfdict.cxx -c $(INCL_PATH) $(HEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

copy: $(DESTDIR)/mfile-root.so

$(DESTDIR)/mfile-root.so: mfile-root.so
	cp mfile-root.so $(DESTDIR)

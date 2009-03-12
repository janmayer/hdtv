# Makefile for comca-root

CPP=g++
CC=gcc
ROOTCINT=rootcint
INCL_PATH=-I/ikpv2/include
CFLAGS=$(shell root-config --cflags) $(INCL_PATH)
LFLAGS=$(shell root-config --glibs) -L/ikpv2/lib -lcomca
SOURCES= CoMCA.cxx
HEADERS= CoMCA.h
OBJ= $(SOURCES:.cxx=.o)
DESTDIR= ../../lib
MODNAME= comca-root

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o

rootdict-$(MODNAME).cxx:  Makefile $(HEADERS)
	$(ROOTCINT) -f rootdict-$(MODNAME).cxx -c $(INCL_PATH) $(HEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<
	
clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

copy: $(DESTDIR)/$(MODNAME).so

$(DESTDIR)/$(MODNAME).so: $(MODNAME).so
	cp $(MODNAME).so $(DESTDIR)

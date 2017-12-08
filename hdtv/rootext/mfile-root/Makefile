# Makefile for mfile-root
MODNAME = mfile-root

SOURCES = MFileHist.cxx VMatrix.cxx MatOp.cxx MFile.cxx matop/matop_adjust.c matop/matop_conv.c matop/matop_project.c
HEADERS = MFileHist.h VMatrix.h MatOp.h MFile.h
OBJ = $(patsubst %.cxx,%.o,$(patsubst %.c,%.o, $(SOURCES)))

CPP = g++
ROOTCLING = rootcling
CFLAGS += $(shell root-config --cflags) -Wall -g -O2 -fPIC
LFLAGS += $(shell root-config --glibs) -lmfile

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

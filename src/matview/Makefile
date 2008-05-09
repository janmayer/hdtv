# Makefile for mattest
#

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags) -I/usr/include/X11
LFLAGS=$(shell root-config --glibs)
SOURCES= MTView.cxx MTViewer.cxx
EXPHEADERS= MTView.h MTViewer.h
HEADERS= $(EXPHEADERS)
OBJ= $(SOURCES:.cxx=.o)

.PHONY: build clean

build: mattest.so

clean:
	-/bin/rm -f matdict.cxx matdict.h matdict.o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

mattest.so: $(OBJ) matdict.o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o mattest.so $(OBJ) matdict.o

matdict.cxx:  Makefile $(EXPHEADERS)
	$(ROOTCINT) -f matdict.cxx -c $(EXPHEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

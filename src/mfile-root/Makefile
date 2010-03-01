# Makefile for mfile-root
include ../Makefile.def

LFLAGS+= -L$(PREFIX)/lib -lmfile
SOURCES= MFileHist.cxx VMatrix.cxx
HEADERS= MFileHist.h VMatrix.h
OBJ= $(SOURCES:.cxx=.o)
MODNAME= mfile-root

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o

rootdict-$(MODNAME).cxx:  Makefile $(HEADERS) LinkDef.h
	$(ROOTCINT) -f rootdict-$(MODNAME).cxx -c -I$(INCL_PATH) $(HEADERS) LinkDef.h

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<
	
clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

copy: $(DESTDIR)/$(MODNAME).so

$(DESTDIR)/$(MODNAME).so: $(MODNAME).so
	cp $(MODNAME).so $(DESTDIR)

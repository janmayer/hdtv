# Makefile for mfile-root
include ../Makefile.def

LFLAGS+= -L$(PREFIX)/lib -lmfile
SOURCES= MFileHist.cxx VMatrix.cxx MatOp.cxx MFile.cxx \
    matop/matop_adjust.c matop/matop_conv.c matop/matop_project.c
HEADERS= MFileHist.h VMatrix.h MatOp.h
OBJ= $(patsubst %.cxx,%.o,$(patsubst %.c,%.o, $(SOURCES)))
MODNAME= mfile-root

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o $(LFLAGS) 

rootdict-$(MODNAME).cxx:  Makefile $(HEADERS) LinkDef.h
	$(ROOTCINT) -f rootdict-$(MODNAME).cxx -c -I$(INCL_PATH) $(HEADERS) LinkDef.h

%.o: %.cxx $(HEADERS) MFile.h Makefile
	$(CPP) $(CFLAGS) -fpic -c -o $@ $<

%.o: %.c $(HEADERS) MFile.h Makefile
	$(CPP) $(CFLAGS) -fpic -c -o $@ $<

clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

copy: $(DESTDIR)/$(MODNAME).so

$(DESTDIR)/$(MODNAME).so: $(MODNAME).so
	mkdir -p $(DESTDIR)
	cp $(MODNAME).so $(DESTDIR)

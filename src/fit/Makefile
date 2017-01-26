# Makefile for HDTV::Fit
include ../Makefile.def

SOURCES= Integral.cxx PolyBg.cxx Param.cxx Fitter.cxx TheuerkaufFitter.cxx EEFitter.cxx Util.cxx
EXPHEADERS= Integral.h Background.h PolyBg.h Param.h Fitter.h TheuerkaufFitter.h EEFitter.h Util.h
HEADERS= $(EXPHEADERS)
OBJ= $(SOURCES:.cxx=.o)
MODNAME= fit

.PHONY: all build copy clean

all: build copy

build: $(MODNAME).so

$(MODNAME).so: $(OBJ) rootdict-$(MODNAME).o Makefile
	$(CPP) -fpic $(CFLAGS) -shared -o $(MODNAME).so $(OBJ) rootdict-$(MODNAME).o  $(LFLAGS)

rootdict-$(MODNAME).cxx:  Makefile $(EXPHEADERS) LinkDef.h
	$(ROOTCINT) -f rootdict-$(MODNAME).cxx -c -noIncludePaths -inlineInputHeader $(EXPHEADERS) LinkDef.h

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	-/bin/rm -f rootdict-$(MODNAME).cxx rootdict-$(MODNAME).h rootdict-$(MODNAME).o rootdict-$(MODNAME)_rdict.pcm
	-/bin/rm -f *~
	-/bin/rm -f $(OBJ)

copy: $(DESTDIR)/$(MODNAME).so

$(DESTDIR)/$(MODNAME).so: $(MODNAME).so
	mkdir -p $(DESTDIR)
	cp $(MODNAME).so $(DESTDIR)
	cp rootdict-$(MODNAME)_rdict.pcm $(DESTDIR)

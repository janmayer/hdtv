# Makefile for HDTV::Display
MODNAME := display

SRC_FILES := $(wildcard *.cxx)
HDR_FILES := $(SRC_FILES:.cxx=.h)
OBJ_FILES := $(SRC_FILES:.cxx=.o)

CPP := g++
ROOTCLING := rootcling
CXXFLAGS += $(shell root-config --cflags) -Wall -g -O2 -fPIC -MMD
LFLAGS += $(shell root-config --glibs)

.PHONY: all build clean

all: build

build: lib$(MODNAME).so

lib$(MODNAME).so: $(OBJ_FILES) $(MODNAME)_rdict.o
	$(CPP) $(CXXFLAGS) -shared -o lib$(MODNAME).so $(OBJ_FILES) $(MODNAME)_rdict.o $(LFLAGS)

$(MODNAME)_rdict.cxx: $(HDR_FILES) LinkDef.h
	# Removed -rml lib$(MODNAME).so as a precaution, failed in fit
	$(ROOTCLING) -f $(MODNAME)_rdict.cxx -noIncludePaths -inlineInputHeader -s lib$(MODNAME).so -rmf lib$(MODNAME).rootmap $(HDR_FILES) LinkDef.h

%.o: %.cxx $(HDR_FILES)
	$(CPP) $(CXXFLAGS) -c -o $@ $<

clean:
	-/bin/rm -f *.o */*.o *.so *.d *.pcm *.rootmap *_rdict.*

-include $(OBJ_FILES:.o=.d)

CPP=g++
CC=gcc
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= LC2Reader.cxx mfile-tiny.c
HEADERS= LC2Reader.h
OBJ= $(SOURCES:.cxx=.o)

.PHONY: clean all

all: lc2reader.so lc2ascii addup

lc2ascii: lc2ascii.c mfile-tiny.c mfile-tiny.h
	$(CC) -o lc2ascii lc2ascii.c mfile-tiny.c
	
addup: addup.c mfile-tiny.c mfile-tiny.h
	$(CC) -o addup addup.c mfile-tiny.c

lc2reader.so: $(OBJ) lc2dict.o
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o lc2reader.so $(OBJ) lc2dict.o

lc2dict.cxx: $(HEADERS)
	$(ROOTCINT) -f lc2dict.cxx -c $(HEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	rm -f lc2dict.cxx lc2dict.h
	rm -f *.o
	rm -f lc2reader.so
	rm -f lc2ascii

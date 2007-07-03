CPP=g++
ROOTCINT=rootcint
CFLAGS=$(shell root-config --cflags)
LFLAGS=$(shell root-config --glibs)
SOURCES= MyClass.cxx
HEADERS= MyClass.h
OBJ= $(SOURCES:.cxx=.o)

.PHONY: clean

test.so: $(OBJ) mydict.o
	$(CPP) -fpic $(CFLAGS) $(LFLAGS) -shared -o test.so $(OBJ) mydict.o

mydict.cxx: $(HEADERS)
	$(ROOTCINT) -f mydict.cxx -c $(HEADERS)

%.o: %.cxx $(HEADERS) Makefile
	$(CPP) $(CFLAGS) -fpic -c $<

clean:
	rm -f mydict.cxx mydict.h
	rm -f *.o
	rm -f test.so
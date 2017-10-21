# global Makefile for hdtv
#
# WARNING: Recursive MAKEs can go very wrong if the different modules
# depend on each other. This is not the case here, the modules are
# completely independent. If two modules depend on each other, they
# should be built by a single Makefile.
MODULES=src

.PHONY: all clean $(MODULES) install doc

all: $(MODULES)

clean:
	$(MAKE) -C src clean
	$(MAKE) -C doc/guide clean

src:
	$(MAKE) -C src

doc:
	$(MAKE) -C doc/guide

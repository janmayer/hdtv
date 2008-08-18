# global Makefile for the C++ part of hdtv
#
# WARNING: Recursive MAKEs can go very wrong if the different modules depend on each other.
# This is not the case here, the modules are completely independent. If two modules depend
# on each other, they should be built by a single Makefile.
MODULES= corr gspec mfile-root

.PHONY: all clean $(MODULES)

all: $(MODULES)

clean:
	$(MAKE) -C corr clean
	$(MAKE) -C gspec clean
	$(MAKE) -C mfile-root clean

corr:
	$(MAKE) -C corr

gspec:
	$(MAKE) -C gspec
	
mfile-root:
	$(MAKE) -C mfile-root

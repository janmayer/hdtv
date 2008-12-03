# global Makefile for the C++ part of hdtv
#
# WARNING: Recursive MAKEs can go very wrong if the different modules depend on each other.
# This is not the case here, the modules are completely independent. If two modules depend
# on each other, they should be built by a single Makefile.
MODULES= display fit mfile-root

.PHONY: all clean $(MODULES)

all: $(MODULES)

clean:
	$(MAKE) -C corr clean
	$(MAKE) -C display clean
	$(MAKE) -C fit clean
	$(MAKE) -C mfile-root clean

corr:
	$(MAKE) -C corr

display:
	$(MAKE) -C display
	
fit:
	$(MAKE) -C fit
	
mfile-root:
	$(MAKE) -C mfile-root

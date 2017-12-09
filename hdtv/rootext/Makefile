MODULES= display fit mfile-root

.PHONY: all clean $(MODULES)

all: $(MODULES)

clean:
	$(MAKE) -C display clean
	$(MAKE) -C fit clean
	$(MAKE) -C mfile-root clean

display:
	$(MAKE) -C display

fit:
	$(MAKE) -C fit

mfile-root:
	$(MAKE) -C mfile-root

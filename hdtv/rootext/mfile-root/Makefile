# Makefile for mfile-root
MODNAME := mfile-root

include ../Makefile.def

LDFLAGS += $(MFILE_LDFLAGS)
LDLIBS += -lmfile

MATOP_SOURCES := $(wildcard matop/*.c)
MATOP_OBJECTS := $(patsubst %.c,%.o,$(MATOP_SOURCES))
MATOP_DEPS    := $(patsubst %.c,%.d,$(MATOP_SOURCES))

SOURCES += $(MATOP_SOURCES)
OBJECTS += $(MATOP_OBJECTS)
DEPS    += $(MATOP_DEPS)

include ../Makefile.body

-include $(MATOP_DEPS)

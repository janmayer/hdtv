# Makefile for mfile-root
MODNAME := mfile-root

include ../Makefile.def

CFLAGS   += $(LIBMFILE_CFLAGS)
CXXFLAGS += $(LIBMFILE_CFLAGS)

LDFLAGS  += $(MFILE_LDFLAGS)

LDLIBS   += $(ROOT_LIBS)
LDLIBS   += -lmfile

ROOT_CLING_FLAGS += $(LIBMFILE_CFLAGS)

MATOP_SOURCES := $(wildcard matop/*.c)
MATOP_OBJECTS := $(patsubst %.c,%.o,$(MATOP_SOURCES))
MATOP_DEPS    := $(patsubst %.c,%.d,$(MATOP_SOURCES))

SOURCES += $(MATOP_SOURCES)
OBJECTS += $(MATOP_OBJECTS)
DEPS    += $(MATOP_DEPS)

include ../Makefile.body

-include $(MATOP_DEPS)

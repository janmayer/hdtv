# Makefile for HDTV::Calibration
MODNAME = calibration

include ../Makefile.def

CFLAGS   += $(LIBX11_CFLAGS)
CXXFLAGS += $(LIBX11_CFLAGS)

LDFLAGS  += $(LIBX11_LDFLAGS)

LDLIBS   += $(ROOT_GLIBS) -lX11

ROOT_CLING_FLAGS += $(LIBX11_CFLAGS)

include ../Makefile.body

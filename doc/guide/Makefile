RST2MAN=rst2man
MANPAGES=$(patsubst %.rst,%.1,$(wildcard hdtv*.rst))

all: $(MANPAGES)

%.1:%.rst
	$(RST2MAN) $< > $@

clean:
	$(RM) $(MANPAGES)

.PHONY: all clean

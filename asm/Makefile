CC ?= clang
CFLAGS ?= -arch arm64

all: combination

combination: combination.s
	$(CC) $(CFLAGS) combination.s -o combination
	cp -f combination main

clean:
	rm -f combination main

.PHONY: all clean

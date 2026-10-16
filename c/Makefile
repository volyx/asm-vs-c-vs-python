CC = clang
CFLAGS = -Wall -Wextra -O3 -arch arm64
SRC = main.c
BIN = combination

.PHONY: all run clean

all: $(BIN)

$(BIN): $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

run: $(BIN)
	./$(BIN)

clean:
	rm -f $(BIN)

PY    = python3
GEN   = gen_combination_class.py
CLASS = Combination
TEST  = test_combination.py

.PHONY: all run test clean disassemble

all: $(CLASS).class

$(CLASS).class: $(GEN)
	$(PY) $(GEN)

run: $(CLASS).class
	java $(CLASS)

test: $(CLASS).class
	$(PY) $(TEST)

disassemble: $(CLASS).class
	javap -c -v $(CLASS)

clean:
	rm -f $(CLASS).class

# Combination in Pure Java Bytecode

A standalone Java program written and assembled directly into JVM bytecode (`Combination.class`) byte-for-byte, without compiling through `javac`.

It reads two integers `k` and `n` from standard input (or command-line arguments) and prints the combination:
$$\binom{n}{k} = C(n, k) = \frac{n!}{k!(n - k)!}$$
as defined on [Wikipedia: Combination](https://en.wikipedia.org/wiki/Combination).

---

## Quick Start (macOS Apple Silicon arm64)

### 1. Run Pre-built Bytecode
The repository includes the pre-assembled `Combination.class`:
```bash
# Read k and n from standard input:
echo "3 5" | java Combination
# Output: 10

# Or run interactively:
java Combination
# (type: 3 5)

# Or pass as command-line arguments:
java Combination 3 5
# Output: 10

# Or via the executable wrapper:
echo "3 5" | ./combination
```

### 2. Re-assemble from Bytecode Source
The bytecode generator `gen_combination_class.py` assembles the `.class` file byte-for-byte using Python:
```bash
make clean
make all       # runs python3 gen_combination_class.py -> Combination.class
make test      # runs the test suite
```

### 3. Inspect Disassembly
```bash
make disassemble   # runs javap -c -v Combination
```

---

## Specification and Algorithm

- **Input**: Two integers `k` and `n` from standard input (or CLI arguments).
- **Semantics**:
  - If $k < 0$ or $n < 0$ or $k > n$: outputs `0` (as defined on Wikipedia: zero when $k > n$).
  - If $k = 0$ or $k = n$: outputs `1`.
  - If $k > n - k$: optimizes by setting $k = n - k$ using symmetry $\binom{n}{k} = \binom{n}{n - k}$.
  - Computes $\binom{n}{k} = \prod_{i=1}^k \frac{n - i + 1}{i}$ using `java.math.BigInteger` to guarantee exact results without 64-bit integer overflow.
- **Output**: The exact combination value followed by a newline.

---

## Bytecode Implementation Details

- **Class Format**: Compliant with JVM Specification (JVMS) Chapter 4 (Java 6 major version 50, supported by all JVMs from Java 6 up to OpenJDK 25+).
- **Constant Pool**: Constant pool table includes classes, UTF-8 strings, NameAndType structures, Fieldrefs (`System.in`, `System.out`, `BigInteger.ZERO`, `BigInteger.ONE`), and Methodrefs (`Scanner.<init>`, `Scanner.nextBigInteger`, `BigInteger.multiply`, `BigInteger.divide`, `PrintStream.println`).
- **Opcodes Used**:
  - Flow control: `ifnull`, `if_icmplt`, `goto`, `iflt`, `ifgt`, `ifeq`, `ifne`, `ifle`, `return`
  - Object creation / method dispatch: `new`, `dup`, `invokespecial`, `invokevirtual`, `getstatic`
  - Local variable / stack manipulation: `aload_0`..`aload_3`, `aload`, `astore_1`..`astore_3`, `astore`, `aaload`, `arraylength`

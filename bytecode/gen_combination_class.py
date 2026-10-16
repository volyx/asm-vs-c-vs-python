#!/usr/bin/env python3
"""gen_combination_class.py — write Combination.class by hand, byte for byte.

Generates a standalone Java classfile directly conforming to JVM Specification (JVMS)
Chapter 4 without invoking `javac`.

The program reads two numbers from standard input: k and n (or from CLI arguments),
and prints the combination C(n, k) = n! / (k! * (n - k)!).
Uses java.math.BigInteger for arbitrary-precision arithmetic without overflow.

Build:
    python3 gen_combination_class.py      # generates Combination.class
Run:
    java Combination                      # reads k and n from stdin
    echo "3 5" | java Combination         # prints 10
    java Combination 3 5                  # prints 10
"""

import struct
import sys


class ConstantPool:
    """Manages constant pool entries with deduplication."""

    def __init__(self):
        self.entries = [None]  # 1-based indexing in JVM classfile
        self.cache = {}

    @property
    def count(self):
        return len(self.entries)

    def _add(self, tag, payload):
        key = (tag, payload)
        if key in self.cache:
            return self.cache[key]
        idx = len(self.entries)
        self.entries.append(bytes([tag]) + payload)
        self.cache[key] = idx
        return idx

    def utf8(self, s: str) -> int:
        b = s.encode("utf-8")
        return self._add(0x01, struct.pack(">H", len(b)) + b)

    def cls(self, name: str) -> int:
        name_idx = self.utf8(name)
        return self._add(0x07, struct.pack(">H", name_idx))

    def string(self, s: str) -> int:
        str_idx = self.utf8(s)
        return self._add(0x08, struct.pack(">H", str_idx))

    def name_and_type(self, name: str, desc: str) -> int:
        n_idx = self.utf8(name)
        d_idx = self.utf8(desc)
        return self._add(0x0C, struct.pack(">HH", n_idx, d_idx))

    def fieldref(self, cls_name: str, name: str, desc: str) -> int:
        c_idx = self.cls(cls_name)
        nt_idx = self.name_and_type(name, desc)
        return self._add(0x09, struct.pack(">HH", c_idx, nt_idx))

    def methodref(self, cls_name: str, name: str, desc: str) -> int:
        c_idx = self.cls(cls_name)
        nt_idx = self.name_and_type(name, desc)
        return self._add(0x0A, struct.pack(">HH", c_idx, nt_idx))


class Assembler:
    """Helper to emit JVM opcodes and resolve relative branch targets."""

    def __init__(self):
        self.code = bytearray()
        self.labels = {}
        self.fixups = []

    def label(self, name: str):
        if name in self.labels:
            raise ValueError(f"Label {name} already defined")
        self.labels[name] = len(self.code)

    def emit(self, *items):
        for item in items:
            if isinstance(item, (bytes, bytearray)):
                self.code.extend(item)
            elif isinstance(item, int):
                self.code.append(item & 0xFF)
            else:
                raise TypeError(f"Cannot emit {type(item)}")

    def u2(self, val: int):
        self.emit(struct.pack(">H", val))

    def branch(self, opcode: int, label_name: str):
        """Emit 3-byte branch instruction with 16-bit signed offset placeholder."""
        self.emit(opcode)
        pos = len(self.code)
        self.emit(0, 0)
        self.fixups.append((pos - 1, pos, label_name))

    def finish(self) -> bytes:
        for inst_pos, op_pos, label_name in self.fixups:
            if label_name not in self.labels:
                raise ValueError(f"Undefined label: {label_name}")
            target = self.labels[label_name]
            offset = target - inst_pos
            struct.pack_into(">h", self.code, op_pos, offset)
        return bytes(self.code)


# JVM Opcodes (JVMS Chapter 6)
ACONST_NULL   = 0x01
ICONST_0      = 0x03
ICONST_1      = 0x04
ICONST_2      = 0x05
ALOAD_0       = 0x2A
ALOAD_1       = 0x2B
ALOAD_2       = 0x2C
ALOAD_3       = 0x2D
ALOAD         = 0x19
AALOAD        = 0x32
ASTORE_1      = 0x4C
ASTORE_2      = 0x4D
ASTORE_3      = 0x4E
ASTORE        = 0x3A
DUP           = 0x59
ARRAYLENGTH   = 0xBE
IFEQ          = 0x99
IFNE          = 0x9A
IFLT          = 0x9B
IFGT          = 0x9D
IFLE          = 0x9E
IF_ICMPLT     = 0xA1
GOTO          = 0xA7
RETURN        = 0xB1
GETSTATIC     = 0xB2
INVOKEVIRTUAL = 0xB6
INVOKESPECIAL = 0xB7
NEW           = 0xBB
IFNULL        = 0xC6

ACC_PUBLIC    = 0x0001
ACC_STATIC    = 0x0008
ACC_SUPER     = 0x0020
MAJOR_VERSION = 50  # Java 6 (fully compatible with Java 6 through Java 25+)


def build_class() -> bytes:
    cp = ConstantPool()

    this_class = cp.cls("Combination")
    super_class = cp.cls("java/lang/Object")

    # Method and field references
    obj_init = cp.methodref("java/lang/Object", "<init>", "()V")
    sys_in = cp.fieldref("java/lang/System", "in", "Ljava/io/InputStream;")
    sys_out = cp.fieldref("java/lang/System", "out", "Ljava/io/PrintStream;")
    println_obj = cp.methodref("java/io/PrintStream", "println", "(Ljava/lang/Object;)V")

    # java.util.Scanner
    sc_cls = cp.cls("java/util/Scanner")
    sc_init = cp.methodref("java/util/Scanner", "<init>", "(Ljava/io/InputStream;)V")
    sc_has_bi = cp.methodref("java/util/Scanner", "hasNextBigInteger", "()Z")
    sc_next_bi = cp.methodref("java/util/Scanner", "nextBigInteger", "()Ljava/math/BigInteger;")

    # java.math.BigInteger
    bi_cls = cp.cls("java/math/BigInteger")
    bi_init_str = cp.methodref("java/math/BigInteger", "<init>", "(Ljava/lang/String;)V")
    bi_zero = cp.fieldref("java/math/BigInteger", "ZERO", "Ljava/math/BigInteger;")
    bi_one = cp.fieldref("java/math/BigInteger", "ONE", "Ljava/math/BigInteger;")
    bi_signum = cp.methodref("java/math/BigInteger", "signum", "()I")
    bi_compareTo = cp.methodref("java/math/BigInteger", "compareTo", "(Ljava/math/BigInteger;)I")
    bi_equals = cp.methodref("java/lang/Object", "equals", "(Ljava/lang/Object;)Z")
    bi_subtract = cp.methodref("java/math/BigInteger", "subtract", "(Ljava/math/BigInteger;)Ljava/math/BigInteger;")
    bi_add = cp.methodref("java/math/BigInteger", "add", "(Ljava/math/BigInteger;)Ljava/math/BigInteger;")
    bi_multiply = cp.methodref("java/math/BigInteger", "multiply", "(Ljava/math/BigInteger;)Ljava/math/BigInteger;")
    bi_divide = cp.methodref("java/math/BigInteger", "divide", "(Ljava/math/BigInteger;)Ljava/math/BigInteger;")

    code_name = cp.utf8("Code")

    # --------------------------------------------------------------------------
    # <init>(): super()
    # --------------------------------------------------------------------------
    init_code = bytes([ALOAD_0, INVOKESPECIAL]) + struct.pack(">H", obj_init) + bytes([RETURN])

    # --------------------------------------------------------------------------
    # main(String[] args):
    # Locals layout:
    #   0: args (String[])
    #   1: k (BigInteger)
    #   2: n (BigInteger)
    #   3: c (BigInteger, combination accumulator / temp)
    #   4: i (BigInteger, loop counter)
    #   5: scanner (java.util.Scanner)
    # --------------------------------------------------------------------------
    asm = Assembler()

    # If args != null and args.length >= 2, parse k from args[0] and n from args[1]
    asm.emit(ALOAD_0)
    asm.branch(IFNULL, "read_stdin")
    asm.emit(ALOAD_0, ARRAYLENGTH, ICONST_2)
    asm.branch(IF_ICMPLT, "read_stdin")

    # Read from args: k = new BigInteger(args[0]), n = new BigInteger(args[1])
    asm.emit(NEW); asm.u2(bi_cls)
    asm.emit(DUP, ALOAD_0, ICONST_0, AALOAD)
    asm.emit(INVOKESPECIAL); asm.u2(bi_init_str)
    asm.emit(ASTORE_1)  # local 1: k

    asm.emit(NEW); asm.u2(bi_cls)
    asm.emit(DUP, ALOAD_0, ICONST_1, AALOAD)
    asm.emit(INVOKESPECIAL); asm.u2(bi_init_str)
    asm.emit(ASTORE_2)  # local 2: n
    asm.branch(GOTO, "compute")

    # Read from standard input (System.in) via java.util.Scanner
    asm.label("read_stdin")
    asm.emit(NEW); asm.u2(sc_cls)
    asm.emit(DUP)
    asm.emit(GETSTATIC); asm.u2(sys_in)
    asm.emit(INVOKESPECIAL); asm.u2(sc_init)
    asm.emit(ASTORE, 5)  # local 5: scanner

    # if (!scanner.hasNextBigInteger()) return;
    asm.emit(ALOAD, 5)
    asm.emit(INVOKEVIRTUAL); asm.u2(sc_has_bi)
    asm.branch(IFEQ, "ret")

    # k = scanner.nextBigInteger()
    asm.emit(ALOAD, 5)
    asm.emit(INVOKEVIRTUAL); asm.u2(sc_next_bi)
    asm.emit(ASTORE_1)

    # if (!scanner.hasNextBigInteger()) return;
    asm.emit(ALOAD, 5)
    asm.emit(INVOKEVIRTUAL); asm.u2(sc_has_bi)
    asm.branch(IFEQ, "ret")

    # n = scanner.nextBigInteger()
    asm.emit(ALOAD, 5)
    asm.emit(INVOKEVIRTUAL); asm.u2(sc_next_bi)
    asm.emit(ASTORE_2)

    # --------------------------------------------------------------------------
    # Computation logic:
    # --------------------------------------------------------------------------
    asm.label("compute")

    # if (k.signum() < 0) return 0;
    asm.emit(ALOAD_1)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_signum)
    asm.branch(IFLT, "print_zero")

    # if (n.signum() < 0) return 0;
    asm.emit(ALOAD_2)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_signum)
    asm.branch(IFLT, "print_zero")

    # if (k.compareTo(n) > 0) return 0;
    asm.emit(ALOAD_1, ALOAD_2)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_compareTo)
    asm.branch(IFGT, "print_zero")

    # if (k.signum() == 0) return 1;
    asm.emit(ALOAD_1)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_signum)
    asm.branch(IFEQ, "print_one")

    # if (k.equals(n)) return 1;
    asm.emit(ALOAD_1, ALOAD_2)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_equals)
    asm.branch(IFNE, "print_one")

    # Symmetry optimization: if k > n - k, then k = n - k
    asm.emit(ALOAD_2, ALOAD_1)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_subtract)  # temp = n - k
    asm.emit(ASTORE_3)
    asm.emit(ALOAD_1, ALOAD_3)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_compareTo)
    asm.branch(IFLE, "loop_init")
    asm.emit(ALOAD_3, ASTORE_1)  # k = n - k

    # c = 1, i = 1
    asm.label("loop_init")
    asm.emit(GETSTATIC); asm.u2(bi_one)
    asm.emit(ASTORE_3)  # local 3: c = 1
    asm.emit(GETSTATIC); asm.u2(bi_one)
    asm.emit(ASTORE, 4)  # local 4: i = 1

    # while (i.compareTo(k) <= 0)
    asm.label("loop_test")
    asm.emit(ALOAD, 4, ALOAD_1)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_compareTo)
    asm.branch(IFGT, "loop_done")

    # c = c.multiply(n.subtract(i).add(BigInteger.ONE)).divide(i)
    asm.emit(ALOAD_3)
    asm.emit(ALOAD_2, ALOAD, 4)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_subtract)  # n - i
    asm.emit(GETSTATIC); asm.u2(bi_one)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_add)       # n - i + 1
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_multiply)  # c * (n - i + 1)
    asm.emit(ALOAD, 4)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_divide)    # / i
    asm.emit(ASTORE_3)                            # c = ...

    # i = i.add(BigInteger.ONE)
    asm.emit(ALOAD, 4)
    asm.emit(GETSTATIC); asm.u2(bi_one)
    asm.emit(INVOKEVIRTUAL); asm.u2(bi_add)
    asm.emit(ASTORE, 4)
    asm.branch(GOTO, "loop_test")

    # Print result c
    asm.label("loop_done")
    asm.emit(GETSTATIC); asm.u2(sys_out)
    asm.emit(ALOAD_3)
    asm.emit(INVOKEVIRTUAL); asm.u2(println_obj)
    asm.emit(RETURN)

    # Print 0
    asm.label("print_zero")
    asm.emit(GETSTATIC); asm.u2(sys_out)
    asm.emit(GETSTATIC); asm.u2(bi_zero)
    asm.emit(INVOKEVIRTUAL); asm.u2(println_obj)
    asm.emit(RETURN)

    # Print 1
    asm.label("print_one")
    asm.emit(GETSTATIC); asm.u2(sys_out)
    asm.emit(GETSTATIC); asm.u2(bi_one)
    asm.emit(INVOKEVIRTUAL); asm.u2(println_obj)
    asm.emit(RETURN)

    asm.label("ret")
    asm.emit(RETURN)

    main_code = asm.finish()

    def method_info(access, name, desc, code, max_stack, max_locals):
        code_attr_body = (
            struct.pack(">HHI", max_stack, max_locals, len(code))
            + code
            + struct.pack(">HH", 0, 0)  # exception_table_length, attributes_count
        )
        code_attr = (
            struct.pack(">HI", code_name, len(code_attr_body))
            + code_attr_body
        )
        return struct.pack(">HHHH", access, cp.utf8(name), cp.utf8(desc), 1) + code_attr

    methods = [
        method_info(ACC_PUBLIC, "<init>", "()V", init_code, 1, 1),
        method_info(ACC_PUBLIC | ACC_STATIC, "main", "([Ljava/lang/String;)V", main_code, 6, 6),
    ]

    # Assemble classfile binary (JVMS 4.1)
    out = bytearray()
    out += b"\xCA\xFE\xBA\xBE"                   # magic
    out += struct.pack(">HH", 0, MAJOR_VERSION)  # minor, major
    out += struct.pack(">H", cp.count)           # constant_pool_count
    for entry in cp.entries[1:]:
        out += entry
    out += struct.pack(">HHH", ACC_PUBLIC | ACC_SUPER, this_class, super_class)
    out += struct.pack(">HHH", 0, 0, len(methods))
    for m in methods:
        out += m
    out += struct.pack(">H", 0)                  # attributes_count
    return bytes(out)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "Combination.class"
    data = build_class()
    with open(path, "wb") as f:
        f.write(data)
    print(f"Emitted {path} ({len(data)} bytes, Java bytecode)")


if __name__ == "__main__":
    main()

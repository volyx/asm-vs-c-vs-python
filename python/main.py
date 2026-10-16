#!/usr/bin/env python3
"""Program to calculate combination C(n, k) for given k and n.

Reads two numbers k and n from standard input (or command-line arguments)
and prints the binomial coefficient / combination C(n, k).
"""

import math
import sys


def combination(k: int, n: int) -> int:
    """Calculate combination C(n, k) = n! / (k! * (n - k)!)."""
    if k < 0 or n < 0 or k > n:
        return 0
    return math.comb(n, k)


def main() -> None:
    if len(sys.argv) >= 3:
        k = int(sys.argv[1])
        n = int(sys.argv[2])
    else:
        tokens = sys.stdin.read().split()
        if len(tokens) < 2:
            sys.exit(1)
        k = int(tokens[0])
        n = int(tokens[1])

    result = combination(k, n)
    print(result)


if __name__ == "__main__":
    main()

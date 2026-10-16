#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define BASE 1000000000ULL
#define MAX_DIGITS 10000

typedef struct {
    uint32_t digits[MAX_DIGITS];
    int len;
} BigInt;

void bigint_init(BigInt *b, uint64_t v) {
    b->len = 0;
    if (v == 0) {
        b->digits[b->len++] = 0;
        return;
    }
    while (v > 0) {
        b->digits[b->len++] = (uint32_t)(v % BASE);
        v /= BASE;
    }
}

void bigint_mul(BigInt *b, uint64_t v) {
    if (v == 0) {
        b->len = 1;
        b->digits[0] = 0;
        return;
    }
    uint64_t carry = 0;
    for (int i = 0; i < b->len; i++) {
        uint64_t cur = (uint64_t)b->digits[i] * v + carry;
        b->digits[i] = (uint32_t)(cur % BASE);
        carry = cur / BASE;
    }
    while (carry > 0 && b->len < MAX_DIGITS) {
        b->digits[b->len++] = (uint32_t)(carry % BASE);
        carry /= BASE;
    }
}

void bigint_div(BigInt *b, uint64_t v) {
    uint64_t rem = 0;
    for (int i = b->len - 1; i >= 0; i--) {
        uint64_t cur = b->digits[i] + rem * BASE;
        b->digits[i] = (uint32_t)(cur / v);
        rem = cur % v;
    }
    while (b->len > 1 && b->digits[b->len - 1] == 0) {
        b->len--;
    }
}

void bigint_print(const BigInt *b) {
    if (b->len == 0) {
        printf("0\n");
        return;
    }
    printf("%u", b->digits[b->len - 1]);
    for (int i = b->len - 2; i >= 0; i--) {
        printf("%09u", b->digits[i]);
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    long long k, n;
    if (argc >= 3) {
        k = atoll(argv[1]);
        n = atoll(argv[2]);
    } else {
        if (scanf("%lld %lld", &k, &n) != 2) {
            return 1;
        }
    }

    if (k < 0 || n < 0 || k > n) {
        printf("0\n");
        return 0;
    }

    if (k == 0 || k == n) {
        printf("1\n");
        return 0;
    }

    if (k > n - k) {
        k = n - k;
    }

    BigInt result;
    bigint_init(&result, 1);

    for (long long i = 1; i <= k; i++) {
        bigint_mul(&result, (uint64_t)(n - k + i));
        bigint_div(&result, (uint64_t)i);
    }

    bigint_print(&result);
    return 0;
}

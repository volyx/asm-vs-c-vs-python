.global _main
.align 2

// Entry point: int main(void)
_main:
    // Stack layout (64 bytes total, 16-byte aligned):
    // [sp + 48]: saved x29 (fp), x30 (lr)
    // [sp + 40]: saved x19
    // [sp + 32]: saved x20
    // [sp + 24]: local variable k (64-bit int)
    // [sp + 16]: local variable n (64-bit int)
    // [sp + 8]:  variadic arg 2 for scanf/printf (on Apple Silicon ARM64 ABI)
    // [sp + 0]:  variadic arg 1 for scanf/printf (on Apple Silicon ARM64 ABI)
    sub sp, sp, #64
    stp x29, x30, [sp, #48]
    add x29, sp, #48
    stp x19, x20, [sp, #32]

    // Read k and n from standard input: scanf("%lld %lld", &k, &n)
    add x8, sp, #24          // address of k
    add x9, sp, #16          // address of n
    stp x8, x9, [sp]         // on Darwin ARM64, variadic args are placed on stack
    adrp x0, fmt_in@PAGE
    add x0, x0, fmt_in@PAGEOFF
    bl _scanf

    // Check if 2 integers were successfully parsed
    cmp w0, #2
    b.ne error_exit

    // Load k and n
    ldr x19, [sp, #24]       // x19 = k
    ldr x20, [sp, #16]       // x20 = n

    // Calculate combination C(n, k)
    // Inputs: x0 = k, x1 = n
    // Output: x0 = result
    mov x0, x19
    mov x1, x20
    bl combination

    // Print result: printf("%llu\n", result)
    str x0, [sp]             // variadic argument on stack for Darwin ARM64
    adrp x0, fmt_out@PAGE
    add x0, x0, fmt_out@PAGEOFF
    bl _printf

    // Normal termination with exit code 0
    mov w0, #0
    b exit_program

error_exit:
    mov w0, #1

exit_program:
    ldp x19, x20, [sp, #32]
    ldp x29, x30, [sp, #48]
    add sp, sp, #64
    ret

// Function: combination
// Computes C(n, k) = n! / (k! * (n - k)!)
// Input:
//   x0: k (signed 64-bit integer)
//   x1: n (signed 64-bit integer)
// Output:
//   x0: combination C(n, k) (unsigned 64-bit integer)
.align 2
combination:
    // If k < 0, return 0
    cmp x0, #0
    b.lt return_zero

    // If n < 0, return 0
    cmp x1, #0
    b.lt return_zero

    // If k > n, return 0 (cannot choose more elements than exist in set)
    cmp x0, x1
    b.gt return_zero

    // If k == 0 or k == n, return 1
    cbz x0, return_one
    cmp x0, x1
    b.eq return_one

    // Optimization: C(n, k) == C(n, n - k)
    // If k > n - k, replace k with n - k
    sub x2, x1, x0          // x2 = n - k
    cmp x0, x2
    csel x0, x2, x0, gt     // x0 = min(k, n - k)

    // ans = 1 (in x2)
    // i = 1 (in x3)
    mov x2, #1              // x2 = ans
    mov x3, #1              // x3 = i

comb_loop:
    cmp x3, x0
    b.gt loop_done

    // term = n - i + 1
    sub x4, x1, x3          // x4 = n - i
    add x4, x4, #1          // x4 = n - i + 1

    // ans = ans * (n - i + 1)
    mul x2, x2, x4

    // ans = ans / i
    udiv x2, x2, x3

    add x3, x3, #1
    b comb_loop

loop_done:
    mov x0, x2
    ret

return_zero:
    mov x0, #0
    ret

return_one:
    mov x0, #1
    ret

.section __TEXT,__cstring,cstring_literals
fmt_in:
    .asciz "%lld %lld"
fmt_out:
    .asciz "%llu\n"

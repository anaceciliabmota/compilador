.section .bss
.lcomm a, 8
.lcomm b, 8
.lcomm d, 8
.lcomm c, 8
.lcomm x, 8

.section .text
pot:
    push %rbp
    mov %rsp, %rbp
    mov 16(%rbp), %rax
    push %rax
    mov 24(%rbp), %rax
    pop %rbx
    xchg %rax, %rbx
    mov %rax, %r8
    mov %rbx, %r9
    mov $1, %rax
Lexp_start_2575557896400:
    cmp $0, %r9
    jle Lexp_end_2575557896400
    imul %r8, %rax
    dec %r9
    jmp Lexp_start_2575557896400
Lexp_end_2575557896400:
    pop %rbp
    ret
.globl _start
_start:
    mov $10, %rax
    mov %rax, a
    mov $3, %rax
    mov %rax, b
    mov $0, %rax
    mov %rax, d
    mov $0, %rax
    mov %rax, c
    mov $0, %rax
    mov %rax, x
    mov $3, %rax
    push %rax
    mov $2, %rax
    push %rax
    call pot
    add $16, %rsp
    mov %rax, d
    mov a, %rax
    push %rax
    mov b, %rax
    pop %rbx
    xchg %rax, %rbx
    cqo
    idiv %rbx
    mov %rdx, %rax
    mov %rax, c
    mov $0, %rax
    mov %rax, x
    mov $1, %rax
    push %rax
    mov $0, %rax
    xor $1, %rax
    pop %rbx
    xchg %rax, %rbx
    and %rbx, %rax
    cmp $0, %rax
    jz Lfalso0
    mov d, %rax
    push %rax
    mov c, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    mov %rax, x
    mov x, %rax
    pop %rbp
    ret
    jmp Lfim0
Lfalso0:
Lfim0:

    call imprime_num
    call sair

.include "runtime.s"

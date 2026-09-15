.section .bss
.lcomm x, 8
.lcomm y, 8

.section .text
.globl _start
_start:
    # x = ...
    mov $7, %rax
    push %rax
    mov $4, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    push %rax
    mov $12, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    mov %rax, x

    # y = ...
    mov x, %rax
    push %rax
    mov $3, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    push %rax
    mov $11, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    mov %rax, y

    # Expressao Final
    mov x, %rax
    push %rax
    mov y, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    push %rax
    mov x, %rax
    push %rax
    mov $11, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    push %rax
    mov y, %rax
    push %rax
    mov $13, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax

    call imprime_num
    call sair

.include "runtime.s"

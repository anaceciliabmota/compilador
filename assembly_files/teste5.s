.section .bss
.lcomm n, 8
.lcomm soma, 8

.section .text
.globl _start
_start:
    mov $1, %rax
    mov %rax, n
    mov $0, %rax
    mov %rax, soma
Linicio0:
    mov n, %rax
    push %rax
    mov $6, %rax
    pop %rbx
    xchg %rax, %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setl %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim0
    mov n, %rax
    push %rax
    mov $3, %rax
    pop %rbx
    xchg %rax, %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setl %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfalso1
    mov soma, %rax
    push %rax
    mov n, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    mov %rax, soma
    jmp Lfim1
Lfalso1:
    mov soma, %rax
    push %rax
    mov $2, %rax
    push %rax
    mov n, %rax
    pop %rbx
    xchg %rax, %rbx
    imul %rbx, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    mov %rax, soma
Lfim1:
    mov n, %rax
    push %rax
    mov $1, %rax
    pop %rbx
    xchg %rax, %rbx
    add %rbx, %rax
    mov %rax, n
    jmp Linicio0
Lfim0:
    mov soma, %rax

    call imprime_num
    call sair

.include "runtime.s"

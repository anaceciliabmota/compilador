   
    .section .text
    .globl _start

_start:
mov $427, %rax
push %rax
mov $7, %rax
mov %rax, %rbx
pop %rax
cqo
idiv %rbx
push %rax
mov $11, %rax
push %rax
mov $231, %rax
push %rax
mov $5, %rax
mov %rax, %rbx
pop %rax
add %rbx, %rax
mov %rax, %rbx
pop %rax
imul %rbx, %rax
mov %rax, %rbx
pop %rax
add %rbx, %rax

    call imprime_num
    call sair

.include "runtime.s"


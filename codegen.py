from tokens import TipoToken
from syntax import Exp, Const, Booleano, Identificador, OpUnario, OpBin, ChamadaFuncao, CmdAtrib, CmdIf, CmdWhile, CmdReturn, DeclaracaoFuncao


def calcular_deslocamentos(decl_funcao: DeclaracaoFuncao) -> dict:
    """
    Retorna um dict nome -> deslocamento_em_bytes relativo a RBP.
    Vars locais ocupam os primeiros L posições, parâmetros vêm depois de RBP salvo e ER.
    - Var local i: i * 8
    - Parâmetro i (sendo p0 o primeiro): (L + 2 + i) * 8
    """
    deslocamentos = {}
    L = len(decl_funcao.vardecls)
    for i, vd in enumerate(decl_funcao.vardecls):
        deslocamentos[vd.nome] = i * 8
    for i, param in enumerate(decl_funcao.params):
        deslocamentos[param[0]] = (L + 2 + i) * 8
    return deslocamentos


def translator(exp: Exp, deslocamentos: dict = {}) -> str:
    codigo = ""
    if isinstance(exp, Const):
        codigo = f"    mov ${exp.valor}, %rax\n"
    elif isinstance(exp, Booleano):
        val = 1 if exp.valor else 0
        codigo = f"    mov ${val}, %rax\n"
    elif isinstance(exp, OpUnario):
        codigo += translator(exp.expressao, deslocamentos)
        if exp.operador == TipoToken.NOT:
            codigo += "    xor $1, %rax\n"
    elif isinstance(exp, Identificador):
        if exp.nome in deslocamentos:
            codigo = f"    mov {deslocamentos[exp.nome]}(%rbp), %rax\n"
        else:
            codigo = f"    mov {exp.nome}, %rax\n"
    elif isinstance(exp, ChamadaFuncao):
        # empilha argumentos em ordem inversa (último primeiro)
        for arg in reversed(exp.args):
            codigo += translator(arg, deslocamentos)
            codigo += "    push %rax\n"
        codigo += f"    call {exp.nome}\n"
        if exp.args:
            codigo += f"    add ${len(exp.args) * 8}, %rsp\n"
    elif isinstance(exp, OpBin):
        codigo += translator(exp.esquerda, deslocamentos)
        codigo += "    push %rax\n"
        codigo += translator(exp.direita, deslocamentos)
        codigo += "    pop %rbx\n"
        codigo += "    xchg %rax, %rbx\n"

        operator = exp.operador
        if operator == TipoToken.SOMA:
            codigo += "    add %rbx, %rax\n"
        elif operator == TipoToken.SUBTRACAO:
            codigo += "    sub %rbx, %rax\n"
        elif operator == TipoToken.MULTIPLICACAO:
            codigo += "    imul %rbx, %rax\n"
        elif operator == TipoToken.DIVISAO:
            codigo += "    cqo\n"
            codigo += "    idiv %rbx\n"
        elif operator == TipoToken.RESTO:
            codigo += "    cqo\n"
            codigo += "    idiv %rbx\n"
            codigo += "    mov %rdx, %rax\n"
        elif operator == TipoToken.EXPONENCIACAO:
            lbl_id = id(exp)
            codigo += f"    mov %rax, %r8\n"
            codigo += f"    mov %rbx, %r9\n"
            codigo += f"    mov $1, %rax\n"
            codigo += f"Lexp_start_{lbl_id}:\n"
            codigo += f"    cmp $0, %r9\n"
            codigo += f"    jle Lexp_end_{lbl_id}\n"
            codigo += f"    imul %r8, %rax\n"
            codigo += f"    dec %r9\n"
            codigo += f"    jmp Lexp_start_{lbl_id}\n"
            codigo += f"Lexp_end_{lbl_id}:\n"
        elif operator == TipoToken.ALL:
            codigo += "    and %rbx, %rax\n"
        elif operator == TipoToken.ANY:
            codigo += "    or %rbx, %rax\n"
        elif operator in (TipoToken.IGUAL_A, TipoToken.MENOR_QUE, TipoToken.MAIOR_QUE):
            instrucao = {
                TipoToken.IGUAL_A:   "setz",
                TipoToken.MENOR_QUE: "setl",
                TipoToken.MAIOR_QUE: "setg",
            }[operator]
            codigo += "    xor %rcx, %rcx\n"
            codigo += "    cmp %rbx, %rax\n"
            codigo += f"    {instrucao} %cl\n"
            codigo += "    mov %rcx, %rax\n"
    return codigo


def gerar_atribuicao(nome: str, exp: Exp, deslocamentos: dict = {}) -> str:
    codigo = translator(exp, deslocamentos)
    if nome in deslocamentos:
        codigo += f"    mov %rax, {deslocamentos[nome]}(%rbp)\n"
    else:
        codigo += f"    mov %rax, {nome}\n"
    return codigo


def gerar_lista_cmds(cmds: list, contador: int, deslocamentos: dict = {}, l_bytes: int = 0) -> tuple:
    codigo = ""
    for c in cmds:
        codigo_c, contador = gerar_cmd(c, contador, deslocamentos, l_bytes)
        codigo += codigo_c
    return codigo, contador


def gerar_cmd(cmd, contador: int, deslocamentos: dict = {}, l_bytes: int = 0) -> tuple:
    if isinstance(cmd, CmdAtrib):
        return gerar_atribuicao(cmd.nome, cmd.exp, deslocamentos), contador
    elif isinstance(cmd, CmdReturn):
        codigo = translator(cmd.exp, deslocamentos)
        if l_bytes > 0:
            codigo += f"    add ${l_bytes}, %rsp\n"
        codigo += "    pop %rbp\n"
        codigo += "    ret\n"
        return codigo, contador
    elif isinstance(cmd, CmdIf):
        n = contador
        contador += 1
        codigo  = translator(cmd.condicao, deslocamentos)
        codigo += f"    cmp $0, %rax\n"
        codigo += f"    jz Lfalso{n}\n"
        codigo_then, contador = gerar_lista_cmds(cmd.corpo_then, contador, deslocamentos, l_bytes)
        codigo += codigo_then
        codigo += f"    jmp Lfim{n}\n"
        codigo += f"Lfalso{n}:\n"
        codigo_else, contador = gerar_lista_cmds(cmd.corpo_else, contador, deslocamentos, l_bytes)
        codigo += codigo_else
        codigo += f"Lfim{n}:\n"
        return codigo, contador
    elif isinstance(cmd, CmdWhile):
        n = contador
        contador += 1
        codigo  = f"Linicio{n}:\n"
        codigo += translator(cmd.condicao, deslocamentos)
        codigo += f"    cmp $0, %rax\n"
        codigo += f"    jz Lfim{n}\n"
        codigo_corpo, contador = gerar_lista_cmds(cmd.corpo, contador, deslocamentos, l_bytes)
        codigo += codigo_corpo
        codigo += f"    jmp Linicio{n}\n"
        codigo += f"Lfim{n}:\n"
        return codigo, contador


def gerar_corpo_funcao(decl_funcao: DeclaracaoFuncao, contador: int = 0) -> tuple:
    nome = decl_funcao.nome
    L = len(decl_funcao.vardecls)
    deslocamentos = calcular_deslocamentos(decl_funcao)

    codigo = f"{nome}:\n"                           # 1. rótulo
    codigo += "    push %rbp\n"                     # 2. salva RBP anterior
    if L > 0:
        codigo += f"    sub ${L * 8}, %rsp\n"       # 3. aloca espaço para vars locais
    codigo += "    mov %rsp, %rbp\n"                # 4. RBP aponta para o registro de ativação

    # 5. calcula e armazena cada variável local
    for vd in decl_funcao.vardecls:
        codigo += translator(vd.exp, deslocamentos)
        codigo += f"    mov %rax, {deslocamentos[vd.nome]}(%rbp)\n"

    # 6. comandos
    l_bytes = L * 8
    codigo_cmds, contador = gerar_lista_cmds(decl_funcao.comandos, contador, deslocamentos, l_bytes)
    codigo += codigo_cmds

    return codigo, contador

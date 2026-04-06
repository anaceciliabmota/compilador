from tokens import TipoToken
from syntax import Exp, Const, Identificador, OpBin, ChamadaFuncao, CmdAtrib, CmdIf, CmdWhile, DeclaracaoFuncao


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
        deslocamentos[param] = (L + 2 + i) * 8
    return deslocamentos


def translator(exp: Exp, deslocamentos: dict = {}) -> str:
    codigo = ""
    if isinstance(exp, Const):
        codigo = f"    mov ${exp.valor}, %rax\n"
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


def gerar_lista_cmds(cmds: list, contador: int, deslocamentos: dict = {}) -> tuple:
    codigo = ""
    for c in cmds:
        codigo_c, contador = gerar_cmd(c, contador, deslocamentos)
        codigo += codigo_c
    return codigo, contador


def gerar_cmd(cmd, contador: int, deslocamentos: dict = {}) -> tuple:
    if isinstance(cmd, CmdAtrib):
        return gerar_atribuicao(cmd.nome, cmd.exp, deslocamentos), contador
    elif isinstance(cmd, CmdIf):
        n = contador
        contador += 1
        codigo  = translator(cmd.condicao, deslocamentos)
        codigo += f"    cmp $0, %rax\n"
        codigo += f"    jz Lfalso{n}\n"
        codigo_then, contador = gerar_lista_cmds(cmd.corpo_then, contador, deslocamentos)
        codigo += codigo_then
        codigo += f"    jmp Lfim{n}\n"
        codigo += f"Lfalso{n}:\n"
        codigo_else, contador = gerar_lista_cmds(cmd.corpo_else, contador, deslocamentos)
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
        codigo_corpo, contador = gerar_lista_cmds(cmd.corpo, contador, deslocamentos)
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
    codigo_cmds, contador = gerar_lista_cmds(decl_funcao.comandos, contador, deslocamentos)
    codigo += codigo_cmds

    # 7. expressão de retorno — resultado em RAX
    codigo += translator(decl_funcao.exp_retorno, deslocamentos)

    if L > 0:
        codigo += f"    add ${L * 8}, %rsp\n"       # 8. libera espaço das vars locais
    codigo += "    pop %rbp\n"                      # 9. restaura RBP anterior
    codigo += "    ret\n"                           # 10. retorna
    return codigo, contador

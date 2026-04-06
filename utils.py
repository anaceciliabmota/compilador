from typing import List
from tokens import TipoToken, Token, ErroSintatico, ErroSemantico, scan_tokens, find_errors
from syntax import (
    Exp, Const, Identificador, OpBin, ChamadaFuncao,
    Declaracao, DeclaracaoFuncao,
    Cmd, CmdAtrib, CmdIf, CmdWhile,
    Programa,
)


def exp_c(tokens, pos):
  esq, pos = exp_a(tokens, pos)
  while pos < len(tokens) and tokens[pos].tipo in [TipoToken.MENOR_QUE, TipoToken.MAIOR_QUE, TipoToken.IGUAL_A]:
      tok = tokens[pos]
      pos += 1
      dir, pos = exp_a(tokens, pos)
      esq = OpBin(tok.tipo, esq, dir)
  return esq, pos

def exp_a(tokens: List[Token], pos: int):
    esq, pos = exp_m(tokens, pos)
    while pos < len(tokens) and tokens[pos].tipo in [TipoToken.SOMA, TipoToken.SUBTRACAO]:
        tok = tokens[pos]
        pos += 1
        dir, pos = exp_m(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

def exp_m(tokens: List[Token], pos: int):
    esq, pos = prim(tokens, pos)
    while pos < len(tokens) and tokens[pos].tipo in [TipoToken.MULTIPLICACAO, TipoToken.DIVISAO]:
        tok = tokens[pos]
        pos += 1
        dir, pos = prim(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

def params_chamada(tokens: List[Token], pos: int):
    args = []
    while tokens[pos].tipo not in (TipoToken.PARENTESE_DIREITO, TipoToken.EOF):
        exp, pos = exp_c(tokens, pos)
        args.append(exp)
        if tokens[pos].tipo == TipoToken.VIRGULA:
            pos += 1
    return args, pos

def chamada_funcao(tokens: List[Token], pos: int):
    nome = tokens[pos].lexema
    pos += 2  # consome nome e '('
    args, pos = params_chamada(tokens, pos)
    if tokens[pos].tipo != TipoToken.PARENTESE_DIREITO:
        raise ErroSintatico("Esperado ')' após argumentos", tokens[pos].posicao)
    return ChamadaFuncao(nome, args), pos + 1

def prim(tokens: List[Token], pos: int):
    if pos >= len(tokens):
        raise ErroSintatico("Fim inesperado da entrada", tokens[-1].posicao)

    tok = tokens[pos]
    if tok.tipo == TipoToken.NUMERO:
        return Const(tok.lexema), pos + 1
    elif tok.tipo == TipoToken.IDENTIFIER:
        if pos + 1 < len(tokens) and tokens[pos + 1].tipo == TipoToken.PARENTESE_ESQUERDO:
            return chamada_funcao(tokens, pos)
        return Identificador(tok.lexema), pos + 1
    elif tok.tipo == TipoToken.PARENTESE_ESQUERDO:
        exp, pos = exp_c(tokens, pos + 1)
        if pos < len(tokens) and tokens[pos].tipo == TipoToken.PARENTESE_DIREITO:
            return exp, pos + 1
        raise ErroSintatico("Esperado parêntese direito ')'", tokens[pos].posicao if pos < len(tokens) else 0)
    else:
        raise ErroSintatico(f"Token inesperado '{tok.lexema}'", tok.posicao)

def vardecl(tokens: List[Token], pos: int):
    pos += 1  # consome 'var'
    if tokens[pos].tipo != TipoToken.IDENTIFIER:
        raise ErroSintatico("Esperado identificador após 'var'", tokens[pos].posicao)
    nome = tokens[pos].lexema
    pos += 1
    if tokens[pos].tipo != TipoToken.EQUAL:
        raise ErroSintatico("Esperado '=' na declaração de variável", tokens[pos].posicao)
    exp, pos = exp_c(tokens, pos + 1)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após declaração de variável", tokens[pos].posicao)
    return Declaracao(nome, exp), pos + 1

def arglist(tokens: List[Token], pos: int):
    params = []
    while tokens[pos].tipo not in (TipoToken.PARENTESE_DIREITO, TipoToken.EOF):
        if tokens[pos].tipo != TipoToken.IDENTIFIER:
            raise ErroSintatico("Esperado identificador na lista de parâmetros", tokens[pos].posicao)
        params.append(tokens[pos].lexema)
        pos += 1
        if tokens[pos].tipo == TipoToken.VIRGULA:
            pos += 1
    return params, pos

def fundecl(tokens: List[Token], pos: int):
    pos += 1  # consome 'fun'
    if tokens[pos].tipo != TipoToken.IDENTIFIER:
        raise ErroSintatico("Esperado nome da função", tokens[pos].posicao)
    nome = tokens[pos].lexema
    pos += 1
    if tokens[pos].tipo != TipoToken.PARENTESE_ESQUERDO:
        raise ErroSintatico("Esperado '(' após nome da função", tokens[pos].posicao)
    pos += 1  # consome '('
    params, pos = arglist(tokens, pos)
    if tokens[pos].tipo != TipoToken.PARENTESE_DIREITO:
        raise ErroSintatico("Esperado ')' após parâmetros", tokens[pos].posicao)
    pos += 1  # consome ')'
    if tokens[pos].tipo != TipoToken.CHAVES_ESQUERDO:
        raise ErroSintatico("Esperado '{' no corpo da função", tokens[pos].posicao)
    pos += 1  # consome '{'
    local_vars = []
    while tokens[pos].tipo == TipoToken.VAR:
        vd, pos = vardecl(tokens, pos)
        local_vars.append(vd)
    cmds, pos = lista_cmds(tokens, pos)
    if tokens[pos].tipo != TipoToken.RETURN:
        raise ErroSintatico("Esperado 'return' no corpo da função", tokens[pos].posicao)
    pos += 1  # consome 'return'
    exp_ret, pos = exp_c(tokens, pos)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após expressão de retorno", tokens[pos].posicao)
    pos += 1  # consome ';'
    if tokens[pos].tipo != TipoToken.CHAVES_DIREITO:
        raise ErroSintatico("Esperado '}' para fechar função", tokens[pos].posicao)
    return DeclaracaoFuncao(nome, params, local_vars, cmds, exp_ret), pos + 1

def decl(tokens: List[Token], pos: int):
    if tokens[pos].tipo == TipoToken.VAR:
        return vardecl(tokens, pos)
    elif tokens[pos].tipo == TipoToken.FUN:
        return fundecl(tokens, pos)
    raise ErroSintatico("Esperado 'var' ou 'fun'", tokens[pos].posicao)

def cmd_atrib(tokens, pos):
    nome = tokens[pos].lexema
    pos += 1  # consome identificador
    if tokens[pos].tipo != TipoToken.EQUAL:
        raise ErroSintatico("Esperado '=' na atribuição", tokens[pos].posicao)
    exp_val, pos = exp_c(tokens, pos + 1)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após atribuição", tokens[pos].posicao)
    return CmdAtrib(nome, exp_val), pos + 1

def lista_cmds(tokens, pos):
  cmds = []
  while tokens[pos].tipo in [TipoToken.IF, TipoToken.WHILE, TipoToken.IDENTIFIER]:
      c, pos = cmd(tokens, pos)
      cmds.append(c)
  return cmds, pos

def cmd(tokens, pos):
    if tokens[pos].tipo == TipoToken.IF:
        return cmd_if(tokens, pos)
    elif tokens[pos].tipo == TipoToken.WHILE:
        return cmd_while(tokens, pos)
    elif tokens[pos].tipo == TipoToken.IDENTIFIER:
        return cmd_atrib(tokens, pos)
    else:
        raise ErroSintatico(f"Comando esperado", tokens[pos].posicao)

def cmd_if(tokens, pos):
    pos += 1  # consome 'if'
    cond, pos = exp_c(tokens, pos)
    pos += 1  # consome '{'
    cmds_true, pos = lista_cmds(tokens, pos)
    pos += 1  # consome '}'
    pos += 1  # consome 'else'
    pos += 1  # consome '{'
    cmds_false, pos = lista_cmds(tokens, pos)
    pos += 1  # consome '}'
    return CmdIf(cond, cmds_true, cmds_false), pos

def cmd_while(tokens, pos):
    pos += 1  # consome 'while'
    cond, pos = exp_c(tokens, pos)
    pos += 1  # consome '{'
    cmds, pos = lista_cmds(tokens, pos)
    pos += 1  # consome '}'
    return CmdWhile(cond, cmds), pos

def programa(tokens: List[Token]):
    pos = 0
    declaracoes = []

    while pos < len(tokens) and tokens[pos].tipo in (TipoToken.VAR, TipoToken.FUN):
        d, pos = decl(tokens, pos)
        declaracoes.append(d)

    if tokens[pos].tipo != TipoToken.MAIN:
        raise ErroSintatico("Esperado 'main'", tokens[pos].posicao)
    pos += 1  # consome 'main'

    if tokens[pos].tipo != TipoToken.CHAVES_ESQUERDO:
        raise ErroSintatico("Esperado '{' após 'main'", tokens[pos].posicao)
    pos += 1  # consome '{'

    cmds, pos = lista_cmds(tokens, pos)

    if tokens[pos].tipo != TipoToken.RETURN:
        raise ErroSintatico("Esperado 'return'", tokens[pos].posicao)
    pos += 1  # consome 'return'

    exp_final, pos = exp_c(tokens, pos)

    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após expressão de retorno", tokens[pos].posicao)
    pos += 1  # consome ';'

    if tokens[pos].tipo != TipoToken.CHAVES_DIREITO:
        raise ErroSintatico("Esperado '}' para fechar o corpo", tokens[pos].posicao)
    pos += 1  # consome '}'

    return Programa(declaracoes, cmds, exp_final), pos
    
def resolve_var(nome: str, tabela_local: dict, tabela_global: dict):
    return tabela_local.get(nome) or tabela_global.get(nome)

def verifica_uso_variaveis(exp: Exp, tabela_local: dict, tabela_global: dict):
    if isinstance(exp, Identificador):
        entrada = resolve_var(exp.nome, tabela_local, tabela_global)
        if entrada is None:
            raise ErroSemantico(f"Variável '{exp.nome}' usada sem ser declarada.")
        if entrada[0] != 'var':
            raise ErroSemantico(f"'{exp.nome}' é uma função e não pode ser usada como variável.")
    elif isinstance(exp, OpBin):
        verifica_uso_variaveis(exp.esquerda, tabela_local, tabela_global)
        verifica_uso_variaveis(exp.direita, tabela_local, tabela_global)
    elif isinstance(exp, ChamadaFuncao):
        entrada = tabela_global.get(exp.nome)
        if entrada is None:
            raise ErroSemantico(f"Função '{exp.nome}' não foi declarada.")
        if entrada[0] != 'fun':
            raise ErroSemantico(f"'{exp.nome}' é uma variável e não pode ser chamada como função.")
        num_params = entrada[1]
        if len(exp.args) != num_params:
            raise ErroSemantico(
                f"Função '{exp.nome}' espera {num_params} argumento(s), mas recebeu {len(exp.args)}."
            )
        for arg in exp.args:
            verifica_uso_variaveis(arg, tabela_local, tabela_global)

def verifica_cmd(cmd, tabela_local: dict, tabela_global: dict):
    if isinstance(cmd, CmdAtrib):
        verifica_uso_variaveis(cmd.exp, tabela_local, tabela_global)
        entrada = resolve_var(cmd.nome, tabela_local, tabela_global)
        if entrada is None:
            raise ErroSemantico(f"Variável '{cmd.nome}' não foi declarada.")
        if entrada[0] != 'var':
            raise ErroSemantico(f"'{cmd.nome}' é uma função e não pode ser atribuída.")
    elif isinstance(cmd, CmdIf):
        verifica_uso_variaveis(cmd.condicao, tabela_local, tabela_global)
        for c in cmd.corpo_then:
            verifica_cmd(c, tabela_local, tabela_global)
        for c in cmd.corpo_else:
            verifica_cmd(c, tabela_local, tabela_global)
    elif isinstance(cmd, CmdWhile):
        verifica_uso_variaveis(cmd.condicao, tabela_local, tabela_global)
        for c in cmd.corpo:
            verifica_cmd(c, tabela_local, tabela_global)

def analise_semantica(prog: Programa):
    tabela_global = {}

    for d in prog.declaracoes:
        if isinstance(d, Declaracao):
            verifica_uso_variaveis(d.exp, {}, tabela_global)
            tabela_global[d.nome] = ('var',)
        elif isinstance(d, DeclaracaoFuncao):
            # registra antes de verificar o corpo — suporta recursão direta
            tabela_local = {p: ('var',) for p in d.params}
            tabela_global[d.nome] = ('fun', len(d.params), tabela_local)
            for vd in d.vardecls:
                verifica_uso_variaveis(vd.exp, tabela_local, tabela_global)
                tabela_local[vd.nome] = ('var',)
            for c in d.comandos:
                verifica_cmd(c, tabela_local, tabela_global)
            verifica_uso_variaveis(d.exp_retorno, tabela_local, tabela_global)

    for c in prog.comandos:
        verifica_cmd(c, {}, tabela_global)
    verifica_uso_variaveis(prog.exp_final, {}, tabela_global)

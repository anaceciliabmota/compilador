from typing import List
from tokens import TipoToken, Token, ErroSintatico, ErroSemantico, scan_tokens, find_errors
from syntax import Exp, Const, Identificador, OpBin, Declaracao, Cmd, CmdAtrib, CmdIf, CmdWhile, Programa


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

def prim(tokens: List[Token], pos: int):
    if pos >= len(tokens):
        raise ErroSintatico("Fim inesperado da entrada", tokens[-1].posicao)
    
    tok = tokens[pos]
    if tok.tipo == TipoToken.NUMERO:
        return Const(tok.lexema), pos + 1
    elif tok.tipo == TipoToken.IDENTIFIER:
        return Identificador(tok.lexema), pos + 1
    elif tok.tipo == TipoToken.PARENTESE_ESQUERDO:
        exp, pos = exp_c(tokens, pos + 1)
        if pos < len(tokens) and tokens[pos].tipo == TipoToken.PARENTESE_DIREITO:
            return exp, pos + 1
        else:
            raise ErroSintatico("Esperado parêntese direito ')'", tokens[pos].posicao if pos < len(tokens) else 0)
    else:
        raise ErroSintatico(f"Token inesperado '{tok.lexema}'", tok.posicao)

def decl(tokens: List[Token], pos: int):
    nome = tokens[pos].lexema
    pos += 1
    if tokens[pos].tipo == TipoToken.EQUAL:
        exp, pos = exp_a(tokens, pos + 1)
        return Declaracao(nome, exp), pos
    else:
        raise ErroSintatico("Esperado sinal de igual '='", tokens[pos].posicao)

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
    
    while pos < len(tokens) and tokens[pos].tipo == TipoToken.IDENTIFIER:
        dec, pos = decl(tokens, pos)
        declaracoes.append(dec)
        if pos < len(tokens) and tokens[pos].tipo == TipoToken.SEMICOLON:
            pos += 1
        else:
            raise ErroSintatico("Esperado ';' após declaração", tokens[pos].posicao)

    if tokens[pos].tipo != TipoToken.CHAVES_ESQUERDO:
        raise ErroSintatico("Esperado '{' para iniciar o corpo", tokens[pos].posicao)
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
    
def verifica_uso_variaveis(exp: Exp, tabela_simbolos: set):
    if isinstance(exp, Identificador):
        if exp.nome not in tabela_simbolos:
            raise ErroSemantico(f"Variável '{exp.nome}' usada sem ser declarada previamente.")
    elif isinstance(exp, OpBin):
        verifica_uso_variaveis(exp.esquerda, tabela_simbolos)
        verifica_uso_variaveis(exp.direita, tabela_simbolos)
    
def verifica_cmd(cmd, tabela_simbolos: set):
    if isinstance(cmd, CmdAtrib):
        verifica_uso_variaveis(cmd.exp, tabela_simbolos)       # lado direito
        if cmd.nome not in tabela_simbolos:                    # lado esquerdo
            raise ErroSemantico(f"Variável '{cmd.nome}' não foi declarada.")
    elif isinstance(cmd, CmdIf):
        verifica_uso_variaveis(cmd.condicao, tabela_simbolos)
        for c in cmd.corpo_then:
            verifica_cmd(c, tabela_simbolos)
        for c in cmd.corpo_else:
            verifica_cmd(c, tabela_simbolos)
    elif isinstance(cmd, CmdWhile):
        verifica_uso_variaveis(cmd.condicao, tabela_simbolos)
        for c in cmd.corpo:
            verifica_cmd(c, tabela_simbolos)

def analise_semantica(prog: Programa):
    tabela_simbolos = set()
    for d in prog.declaracoes:
        verifica_uso_variaveis(d.exp, tabela_simbolos)
        tabela_simbolos.add(d.nome)
    for c in prog.comandos:                                    # <-- novo
        verifica_cmd(c, tabela_simbolos)
    verifica_uso_variaveis(prog.exp_final, tabela_simbolos)

from typing import List
from tokens import TipoToken, Token, ErroSintatico, ErroSemantico
from syntax import (
    Exp, Const, Booleano, Identificador, OpUnario, OpBin, ChamadaFuncao,
    Declaracao, DeclaracaoFuncao,
    Cmd, CmdAtrib, CmdIf, CmdWhile, CmdReturn,
    Programa,
)

def exp_any(tokens, pos):
    esq, pos = exp_all(tokens, pos)
    while pos < len(tokens) and tokens[pos].tipo == TipoToken.ANY:
        tok = tokens[pos]
        pos += 1
        dir, pos = exp_all(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

def exp_all(tokens, pos):
    esq, pos = exp_c(tokens, pos)
    while pos < len(tokens) and tokens[pos].tipo == TipoToken.ALL:
        tok = tokens[pos]
        pos += 1
        dir, pos = exp_c(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

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
    esq, pos = exp_exp(tokens, pos)
    while pos < len(tokens) and tokens[pos].tipo in [TipoToken.MULTIPLICACAO, TipoToken.DIVISAO, TipoToken.RESTO]:
        tok = tokens[pos]
        pos += 1
        dir, pos = exp_exp(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

def exp_exp(tokens: List[Token], pos: int):
    esq, pos = prim(tokens, pos)
    if pos < len(tokens) and tokens[pos].tipo == TipoToken.EXPONENCIACAO:
        tok = tokens[pos]
        pos += 1
        dir, pos = exp_exp(tokens, pos)
        esq = OpBin(tok.tipo, esq, dir)
    return esq, pos

def params_chamada(tokens: List[Token], pos: int):
    args = []
    while tokens[pos].tipo not in (TipoToken.PARENTESE_DIREITO, TipoToken.EOF):
        exp, pos = exp_any(tokens, pos)
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
    elif tok.tipo == TipoToken.TRUE:
        return Booleano(True), pos + 1
    elif tok.tipo == TipoToken.FALSE:
        return Booleano(False), pos + 1
    elif tok.tipo == TipoToken.NOT:
        exp, pos = prim(tokens, pos + 1)
        return OpUnario(TipoToken.NOT, exp), pos
    elif tok.tipo == TipoToken.IDENTIFIER:
        if pos + 1 < len(tokens) and tokens[pos + 1].tipo == TipoToken.PARENTESE_ESQUERDO:
            return chamada_funcao(tokens, pos)
        return Identificador(tok.lexema), pos + 1
    elif tok.tipo == TipoToken.PARENTESE_ESQUERDO:
        exp, pos = exp_any(tokens, pos + 1)
        if pos < len(tokens) and tokens[pos].tipo == TipoToken.PARENTESE_DIREITO:
            return exp, pos + 1
        raise ErroSintatico("Esperado parêntese direito ')'", tokens[pos].posicao if pos < len(tokens) else 0)
    else:
        raise ErroSintatico(f"Token inesperado '{tok.lexema}'", tok.posicao)

def le_tipo(tokens: List[Token], pos: int):
    if tokens[pos].tipo in (TipoToken.TIPO_INT, TipoToken.TIPO_BOOL):
        return tokens[pos].lexema, pos + 1
    raise ErroSintatico("Esperado um tipo ('int' ou 'bool')", tokens[pos].posicao)

def vardecl(tokens: List[Token], pos: int):
    pos += 1  # consome 'var'
    if tokens[pos].tipo != TipoToken.IDENTIFIER:
        raise ErroSintatico("Esperado identificador após 'var'", tokens[pos].posicao)
    nome = tokens[pos].lexema
    pos += 1
    
    if tokens[pos].tipo != TipoToken.DOIS_PONTOS:
        raise ErroSintatico("Esperado ':' após nome da variável para tipagem", tokens[pos].posicao)
    pos += 1
    tipo_var, pos = le_tipo(tokens, pos)

    if tokens[pos].tipo != TipoToken.EQUAL:
        raise ErroSintatico("Esperado '=' na declaração de variável", tokens[pos].posicao)
    exp, pos = exp_any(tokens, pos + 1)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após declaração de variável", tokens[pos].posicao)
    return Declaracao(nome, tipo_var, exp), pos + 1

def arglist(tokens: List[Token], pos: int):
    params = []
    while tokens[pos].tipo not in (TipoToken.PARENTESE_DIREITO, TipoToken.EOF):
        if tokens[pos].tipo != TipoToken.IDENTIFIER:
            raise ErroSintatico("Esperado identificador na lista de parâmetros", tokens[pos].posicao)
        nome_param = tokens[pos].lexema
        pos += 1
        if tokens[pos].tipo != TipoToken.DOIS_PONTOS:
            raise ErroSintatico("Esperado ':' para tipagem do parâmetro", tokens[pos].posicao)
        pos += 1
        tipo_param, pos = le_tipo(tokens, pos)
        
        params.append((nome_param, tipo_param))
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

    if tokens[pos].tipo != TipoToken.SETA:
        raise ErroSintatico("Esperado '->' para tipo de retorno da função", tokens[pos].posicao)
    pos += 1
    tipo_retorno, pos = le_tipo(tokens, pos)

    if tokens[pos].tipo != TipoToken.CHAVES_ESQUERDO:
        raise ErroSintatico("Esperado '{' no corpo da função", tokens[pos].posicao)
    pos += 1  # consome '{'
    
    local_vars = []
    while tokens[pos].tipo == TipoToken.VAR:
        vd, pos = vardecl(tokens, pos)
        local_vars.append(vd)
    
    cmds, pos = lista_cmds(tokens, pos)
    
    if tokens[pos].tipo != TipoToken.CHAVES_DIREITO:
        raise ErroSintatico("Esperado '}' para fechar função", tokens[pos].posicao)
    return DeclaracaoFuncao(nome, params, tipo_retorno, local_vars, cmds), pos + 1

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
    exp_val, pos = exp_any(tokens, pos + 1)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após atribuição", tokens[pos].posicao)
    return CmdAtrib(nome, exp_val), pos + 1

def cmd_return(tokens, pos):
    pos += 1 # consome 'return'
    exp, pos = exp_any(tokens, pos)
    if tokens[pos].tipo != TipoToken.SEMICOLON:
        raise ErroSintatico("Esperado ';' após return", tokens[pos].posicao)
    pos += 1
    return CmdReturn(exp), pos

def lista_cmds(tokens, pos):
  cmds = []
  while tokens[pos].tipo in [TipoToken.IF, TipoToken.WHILE, TipoToken.IDENTIFIER, TipoToken.RETURN]:
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
    elif tokens[pos].tipo == TipoToken.RETURN:
        return cmd_return(tokens, pos)
    else:
        raise ErroSintatico(f"Comando esperado", tokens[pos].posicao)

def cmd_if(tokens, pos):
    pos += 1  # consome 'if'
    cond, pos = exp_any(tokens, pos)
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
    cond, pos = exp_any(tokens, pos)
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

    if tokens[pos].tipo != TipoToken.CHAVES_DIREITO:
        raise ErroSintatico("Esperado '}' para fechar o corpo do main", tokens[pos].posicao)
    pos += 1  # consome '}'

    return Programa(declaracoes, cmds), pos
    
def resolve_var(nome: str, tabela_local: dict, tabela_global: dict):
    return tabela_local.get(nome) or tabela_global.get(nome)

def inferir_tipo(exp: Exp, tabela_local: dict, tabela_global: dict) -> str:
    if isinstance(exp, Const):
        return 'int'
    elif isinstance(exp, Booleano):
        return 'bool'
    elif isinstance(exp, Identificador):
        entrada = resolve_var(exp.nome, tabela_local, tabela_global)
        if entrada is None:
            raise ErroSemantico(f"Variável '{exp.nome}' não declarada.")
        if entrada[0] != 'var':
            raise ErroSemantico(f"'{exp.nome}' é função e não variável.")
        return entrada[1]  # retorna o tipo da variável
    elif isinstance(exp, OpUnario):
        tipo_exp = inferir_tipo(exp.expressao, tabela_local, tabela_global)
        if exp.operador == TipoToken.NOT:
            if tipo_exp != 'bool':
                raise ErroSemantico("Operador 'not' requer booleano.")
            return 'bool'
    elif isinstance(exp, OpBin):
        tipo_esq = inferir_tipo(exp.esquerda, tabela_local, tabela_global)
        tipo_dir = inferir_tipo(exp.direita, tabela_local, tabela_global)
        
        aritm_ops = [TipoToken.SOMA, TipoToken.SUBTRACAO, TipoToken.MULTIPLICACAO, TipoToken.DIVISAO, TipoToken.RESTO, TipoToken.EXPONENCIACAO]
        cmp_ops = [TipoToken.MAIOR_QUE, TipoToken.MENOR_QUE, TipoToken.IGUAL_A]
        log_ops = [TipoToken.ALL, TipoToken.ANY]

        if exp.operador in aritm_ops:
            if tipo_esq != 'int' or tipo_dir != 'int':
                raise ErroSemantico(f"Operador aritmético requer inteiros.")
            return 'int'
        elif exp.operador in log_ops:
            if tipo_esq != 'bool' or tipo_dir != 'bool':
                raise ErroSemantico(f"Operador lógico requer booleanos.")
            return 'bool'
        elif exp.operador in cmp_ops:
            if tipo_esq != tipo_dir:
                raise ErroSemantico(f"Comparação requer tipos iguais.")
            return 'bool'
    elif isinstance(exp, ChamadaFuncao):
        entrada = tabela_global.get(exp.nome)
        if entrada is None:
            raise ErroSemantico(f"Função '{exp.nome}' não declarada.")
        if entrada[0] != 'fun':
            raise ErroSemantico(f"'{exp.nome}' não é função.")
        assinatura_params = entrada[1]
        tipo_retorno = entrada[2]
        if len(exp.args) != len(assinatura_params):
            raise ErroSemantico(f"A função '{exp.nome}' espera {len(assinatura_params)} args.")
        for arg, (nome_param, tipo_param) in zip(exp.args, assinatura_params):
            tipo_arg = inferir_tipo(arg, tabela_local, tabela_global)
            if tipo_arg != tipo_param:
                raise ErroSemantico(f"Argumento '{nome_param}' espera {tipo_param}, obteve {tipo_arg}.")
        return tipo_retorno

def verifica_cmd(cmd, tabela_local: dict, tabela_global: dict, tipo_retorno_esperado: str):
    if isinstance(cmd, CmdAtrib):
        tipo_exp = inferir_tipo(cmd.exp, tabela_local, tabela_global)
        entrada = resolve_var(cmd.nome, tabela_local, tabela_global)
        if entrada is None:
            raise ErroSemantico(f"Variável '{cmd.nome}' não declarada.")
        if entrada[0] != 'var':
            raise ErroSemantico(f"'{cmd.nome}' não é variável.")
        if tipo_exp != entrada[1]:
            raise ErroSemantico(f"Atribuição a '{cmd.nome}' espera '{entrada[1]}', obteve '{tipo_exp}'.")
    elif isinstance(cmd, CmdIf):
        tipo_cond = inferir_tipo(cmd.condicao, tabela_local, tabela_global)
        if tipo_cond != 'bool':
            raise ErroSemantico("Condição do 'if' deve ser booleana.")
        for c in cmd.corpo_then:
            verifica_cmd(c, tabela_local, tabela_global, tipo_retorno_esperado)
        for c in cmd.corpo_else:
            verifica_cmd(c, tabela_local, tabela_global, tipo_retorno_esperado)
    elif isinstance(cmd, CmdWhile):
        tipo_cond = inferir_tipo(cmd.condicao, tabela_local, tabela_global)
        if tipo_cond != 'bool':
            raise ErroSemantico("Condição do 'while' deve ser booleana.")
        for c in cmd.corpo:
            verifica_cmd(c, tabela_local, tabela_global, tipo_retorno_esperado)
    elif isinstance(cmd, CmdReturn):
        tipo_ret = inferir_tipo(cmd.exp, tabela_local, tabela_global)
        if tipo_ret != tipo_retorno_esperado:
            raise ErroSemantico(f"Retorno esperado '{tipo_retorno_esperado}', obteve '{tipo_ret}'.")

def analise_semantica(prog: Programa):
    tabela_global = {}

    for d in prog.declaracoes:
        if isinstance(d, Declaracao):
            tipo_exp = inferir_tipo(d.exp, {}, tabela_global)
            if tipo_exp != d.tipo_var:
                raise ErroSemantico(f"Declaração '{d.nome}' espera '{d.tipo_var}', teve '{tipo_exp}'.")
            tabela_global[d.nome] = ('var', d.tipo_var)
        elif isinstance(d, DeclaracaoFuncao):
            tabela_local = {p[0]: ('var', p[1]) for p in d.params}
            tabela_global[d.nome] = ('fun', d.params, d.tipo_retorno)
            for vd in d.vardecls:
                tipo_exp = inferir_tipo(vd.exp, tabela_local, tabela_global)
                if tipo_exp != vd.tipo_var:
                    raise ErroSemantico(f"Variável local '{vd.nome}' espera '{vd.tipo_var}', obteve '{tipo_exp}'.")
                tabela_local[vd.nome] = ('var', vd.tipo_var)
            for c in d.comandos:
                verifica_cmd(c, tabela_local, tabela_global, d.tipo_retorno)

    for c in prog.comandos:
        # main by default is int in this logic if we want, or whatever. We don't have return in main by default unless user types.
        # But wait, wait! main can have `return`? Yes. Main usually exits or we pop. Let's assume 'int' for main return.
        verifica_cmd(c, {}, tabela_global, 'int')

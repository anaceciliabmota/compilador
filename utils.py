from enum import Enum
from typing import List

class TipoToken(Enum):
    NUMERO = "Numero"
    SOMA = "Soma"
    SUBTRACAO = "Sub"
    MULTIPLICACAO = "Mult"
    DIVISAO = "Div"
    PARENTESE_ESQUERDO = "ParEsq"
    PARENTESE_DIREITO = "ParDir"
    COMENTARIO = "Coment"
    ERROR = "Error"
    EOF = "EOF"
    SEMICOLON = "SemiColon"
    EQUAL = "Assignment"
    IDENTIFIER = "Identifier"

class ErroSintatico(Exception):
    def __init__(self, mensagem, posicao=None):
        self.mensagem = mensagem
        self.posicao = posicao
        super().__init__(self.mensagem)

class ErroSemantico(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)

class Token:
    def __init__(self, tipo: TipoToken, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao

    def __repr__(self):
        return f"<{self.tipo.value}, '{self.lexema}', {self.posicao}>" 

def tipo_token(strings):
    if strings.isdigit():
        return TipoToken.NUMERO
    elif strings == "+":
        return TipoToken.SOMA
    elif strings == "-":    
        return TipoToken.SUBTRACAO
    elif strings == "*":
        return TipoToken.MULTIPLICACAO
    elif strings == "/":
        return TipoToken.DIVISAO
    elif strings == "(":
        return TipoToken.PARENTESE_ESQUERDO
    elif strings == ")":
        return TipoToken.PARENTESE_DIREITO
    elif strings == ";":
        return TipoToken.SEMICOLON
    elif strings == "=":
        return TipoToken.EQUAL
    elif strings in (" ", "\n", "\t"):
        return "WHITESPACE"
    elif strings.isalpha(): 
        return TipoToken.IDENTIFIER
    elif strings.startswith("#"):
        return TipoToken.COMENTARIO
    else:
        return TipoToken.ERROR

def scan_tokens(conteudo):
    tokens = []
    pos = 0
    
    while pos < len(conteudo):
        lexema = conteudo[pos]
        posicao = pos
        
        if conteudo[pos].isdigit():
            for p in range(pos+1, len(conteudo)):
                if conteudo[p].isdigit():
                    lexema += conteudo[p]
                else:
                    pos = p - 1
                    break
        elif conteudo[pos] == "#":
            p = pos+1
            while p < len(conteudo) and conteudo[p] != "\n":
                lexema += conteudo[p]
                p += 1
            pos = p - 1

        tipo = tipo_token(lexema)
        if tipo == TipoToken.IDENTIFIER:
            while pos + 1 < len(conteudo) and (conteudo[pos + 1].isalnum()):
                lexema += conteudo[pos + 1]
                pos += 1
        
        if tipo == "WHITESPACE":
            pos += 1
            continue
        
        token = Token(tipo, lexema, posicao)
        tokens.append(token)
        pos += 1
    
    eof_pos = tokens[-1].posicao + len(tokens[-1].lexema) if tokens else 0
    tokens.append(Token(TipoToken.EOF, '', eof_pos))
    return tokens

def find_errors(tokens):
    erros = [token for token in tokens if token.tipo == TipoToken.ERROR]
    if erros:
        print("Erros léxicos encontrados:")
        for erro in erros:
            print(f"Erro léxico na posição {erro.posicao}: '{erro.lexema}'")
        return True
    return False

# --- CLASSES DA AST ---
class Exp:
    pass

class Const(Exp): 
    def __init__(self, valor):
        self.valor = valor
    def __repr__(self):
        return self.valor

class Identificador(Exp):
    def __init__(self, nome: str):
        self.nome = nome
    def __repr__(self):
        return f"Identificador({self.nome})"

class OpBin(Exp): 
    def __init__(self, operador, esquerda: Exp, direita: Exp):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita
    def __repr__(self):
        return f"OpBin({self.esquerda}, {self.operador.value}, {self.direita})"

class Declaracao:
    def __init__(self, nome: str, exp: Exp):
        self.nome = nome
        self.exp = exp
    def __repr__(self):
        return f"Declaracao({self.nome} = {self.exp})"

class Programa:
    def __init__(self, declaracoes: List[Declaracao], exp_final: Exp):
        self.declaracoes = declaracoes
        self.exp_final = exp_final
    def __repr__(self):
        return f"Programa(Declaracoes: {self.declaracoes}, Resultado: {self.exp_final})"

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
        exp, pos = exp_a(tokens, pos + 1)
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

def programa(tokens: List[Token]):
    pos = 0
    declaracoes = []
    
    while pos < len(tokens) and tokens[pos].tipo == TipoToken.IDENTIFIER:
        dec, pos = decl(tokens, pos)
        declaracoes.append(dec)
        if pos < len(tokens) and tokens[pos].tipo == TipoToken.SEMICOLON:
            pos += 1
        else:
            raise ErroSintatico("Esperado ';' após declaração", tokens[pos].posicao if pos < len(tokens) else 0)
            
    if pos < len(tokens) and tokens[pos].tipo == TipoToken.EQUAL:
        exp_final, pos = exp_a(tokens, pos + 1)
        return Programa(declaracoes, exp_final), pos
    else:
        raise ErroSintatico("Esperado sinal de igual '=' na expressão final", tokens[pos].posicao if pos < len(tokens) else 0)

def verifica_uso_variaveis(exp: Exp, tabela_simbolos: set):
    if isinstance(exp, Identificador):
        if exp.nome not in tabela_simbolos:
            raise ErroSemantico(f"Variável '{exp.nome}' usada sem ser declarada previamente.")
    elif isinstance(exp, OpBin):
        verifica_uso_variaveis(exp.esquerda, tabela_simbolos)
        verifica_uso_variaveis(exp.direita, tabela_simbolos)

def analise_semantica(prog: Programa):
    tabela_simbolos = set()
    for d in prog.declaracoes:
        verifica_uso_variaveis(d.exp, tabela_simbolos)
        tabela_simbolos.add(d.nome)
    verifica_uso_variaveis(prog.exp_final, tabela_simbolos)

# --- TRADUTOR ASSEMBLY ---
def translator(exp: Exp) -> str:
    answer = ""
    if isinstance(exp, Const):
        answer = f"    mov ${exp.valor}, %rax\n"
    elif isinstance(exp, Identificador):
        answer = f"    mov {exp.nome}, %rax\n"
    elif isinstance(exp, OpBin):
        answer += translator(exp.esquerda)
        answer += "    push %rax\n"
        answer += translator(exp.direita)
        answer += "    pop %rbx\n"      # Pop esquerda em RBX
        answer += "    xchg %rax, %rbx\n" # RAX = esquerda, RBX = direita
        
        operator = exp.operador
        if operator == TipoToken.SOMA:
            answer += "    add %rbx, %rax\n"
        elif operator == TipoToken.SUBTRACAO:
            answer += "    sub %rbx, %rax\n"
        elif operator == TipoToken.MULTIPLICACAO:
            answer += "    imul %rbx, %rax\n"
        elif operator == TipoToken.DIVISAO:
            answer += "    cqo\n"
            answer += "    idiv %rbx\n"
    return answer
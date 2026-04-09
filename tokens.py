from enum import Enum


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
    CHAVES_ESQUERDO = "ChavesEsq"
    CHAVES_DIREITO = "ChavesDir"
    MAIOR_QUE = "MaiorQue"
    MENOR_QUE = "MenorQue"
    IGUAL_A = "IgualA"
    RETURN = "Return"
    IF = "If"
    ELSE = "Else"
    WHILE = "While"
    FUN = "Fun"
    VAR = "Var"
    MAIN = "Main"
    VIRGULA = "Virgula"
    ALL = "All"
    ANY = "Any"
    NOT = "Not"
    RESTO = "Resto"
    EXPONENCIACAO = "Exponenciacao"
    TRUE = "True"
    FALSE = "False"
    DOIS_PONTOS = "DoisPontos"
    SETA = "Seta"
    TIPO_INT = "Int"
    TIPO_BOOL = "Bool"


class Token:
    def __init__(self, tipo: TipoToken, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao

    def __repr__(self):
        return f"<{self.tipo.value}, '{self.lexema}', {self.posicao}>"


class ErroSintatico(Exception):
    def __init__(self, mensagem, posicao=None):
        self.mensagem = mensagem
        self.posicao = posicao
        super().__init__(self.mensagem)


class ErroSemantico(Exception):
    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(self.mensagem)


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
    elif strings == ">":
        return TipoToken.MAIOR_QUE
    elif strings == "<":
        return TipoToken.MENOR_QUE
    elif strings == "{":
        return TipoToken.CHAVES_ESQUERDO
    elif strings == "}":
        return TipoToken.CHAVES_DIREITO
    elif strings == ",":
        return TipoToken.VIRGULA
    elif strings == "%":
        return TipoToken.RESTO
    elif strings == "^":
        return TipoToken.EXPONENCIACAO
    elif strings == ":":
        return TipoToken.DOIS_PONTOS
    else:
        return TipoToken.ERROR


def identify_comand(lexema):
    keywords = {
        "if": TipoToken.IF,
        "else": TipoToken.ELSE,
        "while": TipoToken.WHILE,
        "return": TipoToken.RETURN,
        "fun": TipoToken.FUN,
        "var": TipoToken.VAR,
        "main": TipoToken.MAIN,
        "all": TipoToken.ALL,
        "any": TipoToken.ANY,
        "not": TipoToken.NOT,
        "true": TipoToken.TRUE,
        "false": TipoToken.FALSE,
        "int": TipoToken.TIPO_INT,
        "bool": TipoToken.TIPO_BOOL,
    }
    return keywords.get(lexema, TipoToken.IDENTIFIER)


def scan_tokens(conteudo):
    tokens = []
    pos = 0

    while pos < len(conteudo):
        lexema = conteudo[pos]
        posicao = pos

        if conteudo[pos].isdigit():
            for p in range(pos + 1, len(conteudo)):
                if conteudo[p].isdigit():
                    lexema += conteudo[p]
                else:
                    pos = p - 1
                    break
        elif conteudo[pos] == "#":
            p = pos + 1
            while p < len(conteudo) and conteudo[p] != "\n":
                lexema += conteudo[p]
                p += 1
            pos = p - 1

        tipo = tipo_token(lexema)
        if tipo == TipoToken.IDENTIFIER:
            while pos + 1 < len(conteudo) and conteudo[pos + 1].isalnum():
                lexema += conteudo[pos + 1]
                pos += 1
            tipo = identify_comand(lexema)

        if tipo == TipoToken.EQUAL:
            if conteudo[pos + 1] == "=":
                lexema += conteudo[pos + 1]
                pos += 1
                tipo = TipoToken.IGUAL_A
            
        if tipo == TipoToken.SUBTRACAO:
            if pos + 1 < len(conteudo) and conteudo[pos + 1] == ">":
                lexema += conteudo[pos + 1]
                pos += 1
                tipo = TipoToken.SETA

        if tipo in ("WHITESPACE", TipoToken.COMENTARIO):
            pos += 1
            continue

        tokens.append(Token(tipo, lexema, posicao))
        pos += 1

    eof_pos = tokens[-1].posicao + len(tokens[-1].lexema) if tokens else 0
    tokens.append(Token(TipoToken.EOF, "", eof_pos))
    return tokens


def find_errors(tokens):
    erros = [token for token in tokens if token.tipo == TipoToken.ERROR]
    if erros:
        print("Erros léxicos encontrados:")
        for erro in erros:
            print(f"Erro léxico na posição {erro.posicao}: '{erro.lexema}'")
        return True
    return False

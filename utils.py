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
    elif strings == " ":
        return "WHITESPACE"
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
        
        if tipo == "WHITESPACE":
            pos += 1
            continue
        
        token = Token(tipo, lexema, posicao)
        tokens.append(token)
        pos += 1
    
    return tokens

def find_errors(tokens):
    erros = [token for token in tokens if token.tipo == TipoToken.ERROR]
    
    if erros:
        print("Erros léxicos encontrados:")
        for erro in erros:
            print(f"Erro léxico na posição {erro.posicao}: '{erro.lexema}'")
        return True
    
    return False

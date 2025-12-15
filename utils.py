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


class Token:
    def __init__(self, tipo: TipoToken, lexema, posicao):
        self.tipo = tipo
        self.lexema = lexema
        self.posicao = posicao

    def __repr__(self):
        return f"<{self.tipo.value}, '{self.lexema}', {self.posicao}>" 
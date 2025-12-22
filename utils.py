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

def analisa_operador(tokens, pos):
    token = tokens[pos]
    if token.tipo == TipoToken.SOMA:
        return (TipoToken.SOMA, pos)
    elif token.tipo == TipoToken.SUBTRACAO:
        return (TipoToken.SUBTRACAO, pos)
    elif token.tipo == TipoToken.MULTIPLICACAO:
        return (TipoToken.MULTIPLICACAO, pos)
    elif token.tipo == TipoToken.DIVISAO:
        return (TipoToken.DIVISAO, pos)
    else:
        raise ValueError(f"Operador inválido: {token}")


class Exp:
    pass

class Const(Exp): 
    def __init__(self, valor):
        self.valor = valor

    def avaliar(self):
        return int(self.valor)    
    def __repr__(self):
        return self.valor

class OpBin(Exp): 
    def __init__(self, operador, esquerda: Const, direita: Const):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita

    def avaliar(self):
        esq = self.esquerda.avaliar()
        dir = self.direita.avaliar()

        if self.operador == TipoToken.SOMA:
            return esq + dir
        elif self.operador == TipoToken.SUBTRACAO:
            return esq - dir
        elif self.operador == TipoToken.MULTIPLICACAO:
            return esq * dir
        elif self.operador == TipoToken.DIVISAO:
            return esq / dir
        else:
            raise ValueError(f"Operador inválido: {self.operador}")

    def __repr__(self):
        return f"OpBin({self.esquerda}, {self.operador.value}, {self.direita})"


def analisa_exp(tokens, pos):
    if tokens[pos].tipo == TipoToken.NUMERO:
        return Const(tokens[pos].lexema), pos 
    elif tokens[pos].tipo == TipoToken.PARENTESE_ESQUERDO:
        op_esquerdo, pos = analisa_exp(tokens, pos + 1)
        operador, pos = analisa_operador(tokens, pos + 1)   
        op_direito, pos = analisa_exp(tokens, pos + 1)

        if tokens[pos+1].tipo == TipoToken.PARENTESE_DIREITO:
            return OpBin(operador, op_esquerdo, op_direito), pos + 1
        else:
            raise ValueError(f"Token inválido: {tokens[pos]}")

    else:
        raise ValueError(f"Token inválido: {tokens[pos]}")
   


def read_tree(exp: Exp, indent=0, prefix="", is_last=True): #Lê a arvore de forma estruturada
    """Retorna representação em string da árvore sintática de forma hierárquica"""
    # Mapeamento de operadores para símbolos
    ops = {
        TipoToken.SOMA: '+',
        TipoToken.SUBTRACAO: '-',
        TipoToken.MULTIPLICACAO: '*',
        TipoToken.DIVISAO: '/'
    }
    
    resultado = []
    
    if isinstance(exp, Const):
        # Nó folha (constante)
        connector = "└── " if is_last else "├── "
        resultado.append(f"{prefix}{connector}{exp.valor}")
    elif isinstance(exp, OpBin):
        # Nó operador
        op_symbol = ops.get(exp.operador, '?')
        connector = "└── " if is_last else "├── "
        resultado.append(f"{prefix}{connector}{op_symbol}")
        
        # Preparar prefixo para os filhos
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        
        # Processar filho esquerdo
        if isinstance(exp.esquerda, Const):
            resultado.append(f"{new_prefix}├── {exp.esquerda.valor}")
        else:
            resultado.append(read_tree(exp.esquerda, indent + 1, new_prefix, False))
        
        # Processar filho direito
        if isinstance(exp.direita, Const):
            resultado.append(f"{new_prefix}└── {exp.direita.valor}")
        else:
            resultado.append(read_tree(exp.direita, indent + 1, new_prefix, True))
    else:
        raise ValueError(f"Expressão inválida: {exp}")
    
    return "\n".join(resultado)
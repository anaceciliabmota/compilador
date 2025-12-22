from enum import Enum
import sys

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

class ErroSintatico(Exception):
    def __init__(self, mensagem, posicao=None):
        self.mensagem = mensagem
        self.posicao = posicao
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
    
    # token EOF para parsing
    if tokens:
        eof_pos = tokens[-1].posicao + len(tokens[-1].lexema)
    else:
        eof_pos = 0
    tokens.append(Token(TipoToken.EOF, '', eof_pos))
    
    return tokens

def find_errors(tokens):
    """léxicos"""
    erros = [token for token in tokens if token.tipo == TipoToken.ERROR]
    
    if erros:
        print("Erros léxicos encontrados:")
        for erro in erros:
            print(f"Erro léxico na posição {erro.posicao}: '{erro.lexema}'")
        return True
    
    return False

def validar_parenteses(tokens):
    contador = 0
    posicoes_abertura = []
    
    for token in tokens:
        if token.tipo == TipoToken.PARENTESE_ESQUERDO:
            contador += 1
            posicoes_abertura.append(token.posicao)
        elif token.tipo == TipoToken.PARENTESE_DIREITO:
            contador -= 1
            if contador < 0:
                raise ErroSintatico(
                    f"Parêntese direito sem correspondente na posição {token.posicao}",
                    token.posicao
                )
    
    if contador > 0:
        raise ErroSintatico(
            f"Parêntese esquerdo sem fechamento na posição {posicoes_abertura[-1]}",
            posicoes_abertura[-1]
        )
    
    return True

def analisa_operador(tokens, pos):
    if pos >= len(tokens):
        raise ErroSintatico(
            "Esperado operador, mas fim da entrada alcançado",
            tokens[-1].posicao if tokens else 0
        )
    
    token = tokens[pos]
    
    if token.tipo in [TipoToken.SOMA, TipoToken.SUBTRACAO, 
                      TipoToken.MULTIPLICACAO, TipoToken.DIVISAO]:
        return (token.tipo, pos)
    else:
        raise ErroSintatico(
            f"Esperado operador (+, -, *, /), mas encontrado '{token.lexema}' na posição {token.posicao}",
            token.posicao
        )


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
            if dir == 0:
                raise ZeroDivisionError("Divisão por zero")
            return esq // dir
        else:
            raise ValueError(f"Operador inválido: {self.operador}")

    def __repr__(self):
        return f"OpBin({self.esquerda}, {self.operador.value}, {self.direita})"


def analisa_parenteses(tokens, pos, operador, op_esquerdo, op_direito):
    if pos >= len(tokens):
        raise ErroSintatico(
            "Esperado parêntese direito ')' mas fim da entrada alcançado",
            tokens[-1].posicao if tokens else 0
        )
    
    token = tokens[pos]
    
    if token.tipo == TipoToken.PARENTESE_DIREITO:
        return OpBin(operador, op_esquerdo, op_direito), pos
    elif token.tipo == TipoToken.EOF:
        raise ErroSintatico(
            "Esperado parêntese direito ')' mas fim da entrada alcançado",
            token.posicao
        )
    else:
        raise ErroSintatico(
            f"Esperado parêntese direito ')' mas encontrado '{token.lexema}' na posição {token.posicao}",
            token.posicao
        )


def analisa_exp(tokens, pos):
    if pos >= len(tokens):
        raise ErroSintatico(
            "Esperado expressão, mas fim da entrada alcançado",
            tokens[-1].posicao if tokens else 0
        )
    
    token = tokens[pos]
    
    if token.tipo == TipoToken.NUMERO:
        return Const(token.lexema), pos
    
    elif token.tipo == TipoToken.PARENTESE_ESQUERDO:
        # Analisa operando esquerdo
        op_esquerdo, pos = analisa_exp(tokens, pos + 1)
        
        operador, pos = analisa_operador(tokens, pos + 1)
        
        # Analisa operando direito
        op_direito, pos = analisa_exp(tokens, pos + 1)
        
        # Valida fechamento do parêntese
        return analisa_parenteses(tokens, pos + 1, operador, op_esquerdo, op_direito)
    
    elif token.tipo == TipoToken.PARENTESE_DIREITO:
        raise ErroSintatico(
            f"Parêntese direito inesperado na posição {token.posicao}",
            token.posicao
        )
    elif token.tipo in [TipoToken.SOMA, TipoToken.SUBTRACAO, 
                        TipoToken.MULTIPLICACAO, TipoToken.DIVISAO]:
        raise ErroSintatico(
            f"Operador '{token.lexema}' inesperado na posição {token.posicao}. Expressão deve começar com número ou parêntese esquerdo",
            token.posicao
        )
    elif token.tipo == TipoToken.COMENTARIO:
        raise ErroSintatico(
            f"Comentário inesperado na posição {token.posicao}",
            token.posicao
        )
    elif token.tipo == TipoToken.EOF:
        raise ErroSintatico(
            "Expressão vazia ou incompleta",
            token.posicao
        )
    else:
        raise ErroSintatico(
            f"Token inválido '{token.lexema}' na posição {token.posicao}",
            token.posicao
        )
   


def read_tree(exp: Exp, indent=0, prefix="", is_last=True): #Lê a arvore de forma estruturada [ gpt :D ]
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
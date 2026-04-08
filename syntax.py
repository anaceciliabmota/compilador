from typing import List


class Exp:
    pass

class Const(Exp):
    def __init__(self, valor):
        self.valor = valor
    def __repr__(self):
        return self.valor

class Booleano(Exp):
    def __init__(self, valor: bool):
        self.valor = valor
    def __repr__(self):
        return str(self.valor).lower()

class Identificador(Exp):
    def __init__(self, nome: str):
        self.nome = nome
    def __repr__(self):
        return f"Identificador({self.nome})"

class OpUnario(Exp):
    def __init__(self, operador, expressao: Exp):
        self.operador = operador
        self.expressao = expressao
    def __repr__(self):
        return f"OpUnario({self.operador.value}, {self.expressao})"

class OpBin(Exp):
    def __init__(self, operador, esquerda: Exp, direita: Exp):
        self.operador = operador
        self.esquerda = esquerda
        self.direita = direita
    def __repr__(self):
        return f"OpBin({self.esquerda}, {self.operador.value}, {self.direita})"

class ChamadaFuncao(Exp):
    def __init__(self, nome: str, args: List[Exp]):
        self.nome = nome
        self.args = args
    def __repr__(self):
        return f"ChamadaFuncao({self.nome}, {self.args})"

class Declaracao:
    def __init__(self, nome: str, tipo_var: str, exp: Exp):
        self.nome = nome
        self.tipo_var = tipo_var
        self.exp = exp
    def __repr__(self):
        return f"Declaracao({self.nome}: {self.tipo_var} = {self.exp})"

class DeclaracaoFuncao:
    def __init__(self, nome: str, params: List[tuple], tipo_retorno: str, vardecls: List[Declaracao], comandos: list):
        self.nome = nome
        self.params = params
        self.tipo_retorno = tipo_retorno
        self.vardecls = vardecls
        self.comandos = comandos
    def __repr__(self):
        return f"DeclaracaoFuncao({self.nome}, params={self.params}, retorno={self.tipo_retorno}, vardecls={self.vardecls}, comandos={self.comandos})"

class Cmd:
    pass

class CmdReturn(Cmd):
    def __init__(self, exp: Exp):
        self.exp = exp
    def __repr__(self):
        return f"CmdReturn({self.exp})"

class CmdAtrib(Cmd):
    def __init__(self, nome: str, exp: Exp):
        self.nome = nome
        self.exp = exp
    def __repr__(self):
        return f"CmdAtrib({self.nome} = {self.exp})"

class CmdIf(Cmd):
    def __init__(self, condicao: Exp, corpo_then: list, corpo_else: list):
        self.condicao = condicao
        self.corpo_then = corpo_then
        self.corpo_else = corpo_else
    def __repr__(self):
        return f"CmdIf({self.condicao}, {self.corpo_then}, {self.corpo_else})"

class CmdWhile(Cmd):
    def __init__(self, condicao: Exp, corpo: list):
        self.condicao = condicao
        self.corpo = corpo
    def __repr__(self):
        return f"CmdWhile({self.condicao}, {self.corpo})"

class Programa:
    def __init__(self, declaracoes: list, comandos: List[Cmd]):
        self.declaracoes = declaracoes
        self.comandos = comandos
    def __repr__(self):
        return f"Programa(Declaracoes: {self.declaracoes}, Comandos: {self.comandos})"

from typing import List


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

class ChamadaFuncao(Exp):
    def __init__(self, nome: str, args: List[Exp]):
        self.nome = nome
        self.args = args
    def __repr__(self):
        return f"ChamadaFuncao({self.nome}, {self.args})"

class Declaracao:
    def __init__(self, nome: str, exp: Exp):
        self.nome = nome
        self.exp = exp
    def __repr__(self):
        return f"Declaracao({self.nome} = {self.exp})"

class DeclaracaoFuncao:
    def __init__(self, nome: str, params: List[str], vardecls: List[Declaracao], comandos: list, exp_retorno: Exp):
        self.nome = nome
        self.params = params
        self.vardecls = vardecls
        self.comandos = comandos
        self.exp_retorno = exp_retorno
    def __repr__(self):
        return f"DeclaracaoFuncao({self.nome}, params={self.params}, vardecls={self.vardecls}, comandos={self.comandos}, exp_retorno={self.exp_retorno})"

class Cmd:
    pass

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
    def __init__(self, declaracoes: list, comandos: List[Cmd], exp_final: Exp):
        self.declaracoes = declaracoes
        self.comandos = comandos
        self.exp_final = exp_final
    def __repr__(self):
        return f"Programa(Declaracoes: {self.declaracoes}, Comandos: {self.comandos}, Resultado: {self.exp_final})"

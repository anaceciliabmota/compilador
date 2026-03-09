import sys
from utils import (Token, tipo_token, TipoToken, scan_tokens, find_errors, 
                   analisa_exp, read_tree, validar_parenteses, ErroSintatico, translator, exp_a)


prologo = """   
    .section .text
    .globl _start

_start:
"""
epilogo = """
    call imprime_num
    call sair

.include "runtime.s"
"""


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <arquivo_entrada>")
        sys.exit(1)
    
    nome_arquivo = sys.argv[1]
    
    try:
        with open(nome_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{nome_arquivo}' não encontrado.")
        sys.exit(1)
    
    # Análise léxica
    tokens = scan_tokens(conteudo)
    
    if find_errors(tokens):
        print("Compilação abortada devido a erros léxicos.")
        sys.exit(1)

    try:
        # Valida parenteses balanceados
        exp, pos = exp_a(tokens, 0)
        str = translator(exp)

        print(prologo + str + epilogo)
    
    except ErroSintatico as e:
        print(f"\n\nErro sintático: {e.mensagem}")
        print("Compilação abortada devido a erros sintáticos.")
        sys.exit(1)
    except ZeroDivisionError:
        print("\n\nErro semântico: Divisão por zero detectada.")
        print("Compilação abortada devido a erro semântico.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro inesperado: {str(e)}")
        sys.exit(1)
    

if __name__ == "__main__":
    main()
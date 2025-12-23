import sys
from utils import (Token, tipo_token, TipoToken, scan_tokens, find_errors, 
                   analisa_exp, read_tree, validar_parenteses, ErroSintatico)

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
    
    print("--------------\nAnálise léxica:")
    tokens_visiveis = [t for t in tokens if t.tipo not in [TipoToken.EOF]]
    for token in tokens_visiveis:
        print(token)
    
    try:
        # Valida parenteses balanceados
        validar_parenteses(tokens)
        
        # Análise sintática
        print("\n\n--------------\nAnálise sintática:")
        exp, pos = analisa_exp(tokens, 0)
        
        pos += 1
        while pos < len(tokens):
            token = tokens[pos]
            if token.tipo not in [TipoToken.COMENTARIO, TipoToken.EOF]:
                raise ErroSintatico(
                    f"Token inesperado após expressão: '{token.lexema}' na posição {token.posicao}",
                    token.posicao
                )
            pos += 1
        
        # árvore sintática
        print(read_tree(exp))
        
        print("\n\n--------------\nValor da expressão:")
        resultado = exp.avaliar()
        print(resultado)
        
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
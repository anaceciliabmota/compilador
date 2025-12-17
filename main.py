import sys
from utils import Token, tipo_token, TipoToken,  scan_tokens, find_errors

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
    
    tokens = scan_tokens(conteudo)
    
    if find_errors(tokens):
        print("Compilação abortada devido a erros léxicos.")
        sys.exit(1)
    
    print("Análise léxica bem-sucedida:")
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()
import sys
from utils import Token, tipo_token

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py  <arquivo_entrada>")
        sys.exit(1)
    nome_arquivo = sys.argv[1]
    with open(nome_arquivo, 'r') as arquivo:
        conteudo = arquivo.read()
    
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
            while p < len(conteudo) and conteudo[pos] != "\n":
                lexema += conteudo[p]
                p += 1
            pos = p - 1
        
        tipo = tipo_token(lexema)
        if tipo == "WHITESPACE":
            pos += 1
            continue

        token = Token(tipo, lexema, posicao)
        print(token)

        pos += 1


if __name__ == "__main__":
    main()

        


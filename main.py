import sys
import os
import subprocess
from tokens import ErroSintatico, ErroSemantico, scan_tokens, find_errors
from utils import programa, analise_semantica, translator

epilogo = """
    call imprime_num
    call sair

.include "runtime.s"
"""

def gerar_codigo_programa(prog):
    codigo_asm = ""
    
    # 1.(BSS)
    codigo_asm += ".section .bss\n"
    for decl in prog.declaracoes:
        codigo_asm += f".lcomm {decl.nome}, 8\n"
        
    # 2. Ponto de Entrada 
    codigo_asm += "\n.section .text\n"
    codigo_asm += ".globl _start\n"
    codigo_asm += "_start:\n"
    
    # 3. Declarações
    for decl in prog.declaracoes:
        codigo_asm += f"    # {decl.nome} = ...\n"
        codigo_asm += translator(decl.exp)
        codigo_asm += f"    mov %rax, {decl.nome}\n\n"
        
    # 4. Resultado
    codigo_asm += "    # Expressao Final\n"
    codigo_asm += translator(prog.exp_final)
    
    # 5. Finaliza a execução
    codigo_asm += epilogo
    return codigo_asm

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
    for token in tokens:
        print(token)

    if find_errors(tokens):
        print("Compilação abortada devido a erros léxicos.")
        sys.exit(1)
        
    try:
        p, pos = programa(tokens)
        print("Árvore Sintática gerada com sucesso!")
        print(p)
        exit(0)
        
        analise_semantica(p)
        print("Análise Semântica (Verificação de Variáveis) aprovada!")
        
        assembly = gerar_codigo_programa(p)
        
        nome_sem_pasta = os.path.basename(nome_arquivo)
        base_name = os.path.splitext(nome_sem_pasta)[0]

        arquivo_s = os.path.join("assembly_files", f"{base_name}.s")
        arquivo_o = os.path.join("object_files", f"{base_name}.o")
        arquivo_exe = os.path.join("executables", base_name)

    
        with open(arquivo_s, 'w') as f:
            f.write(assembly)            
        print(f"Compilação concluída! Assembly salvo em: '{arquivo_s}'")

        try:
            subprocess.run(["as", arquivo_s, "-o", arquivo_o], check=True)
            print(f"Arquivo objeto montado em: '{arquivo_o}'")
            
            subprocess.run(["ld", arquivo_o, "-o", arquivo_exe], check=True)
            print(f"Executável gerado com sucesso em: '{arquivo_exe}'")
            
            print(f"\nPara ver o resultado, execute o comando abaixo:")
            print(f"./{arquivo_exe}")
            
        except subprocess.CalledProcessError:
            print("\n[ERRO] Ocorreu uma falha no Assembler ('as') ou Linker ('ld').")
            sys.exit(1)
    
    except ErroSintatico as e:
        print(f"\n[ERRO SINTÁTICO] {e.mensagem}")
        sys.exit(1)
    except ErroSemantico as e:
        print(f"\n[ERRO SEMÂNTICO] {e.mensagem}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERRO INESPERADO] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
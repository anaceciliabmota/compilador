#!/bin/bash

# Verifica se o número correto de argumentos foi fornecido
if [ "$#" -ne 3 ]; then
    echo "Uso: $0 <arquivo_de_entrada> <arquivo_assembly_saida.s> <nome_do_executavel>"
    exit 1
fi

# Argumentos
ARQUIVO_ENTRADA=$1
ARQUIVO_ASSEMBLY=$2
ARQUIVO_EXECUTAVEL=$3

# Diretórios para organizar os arquivos
DIR_ASSEMBLY="assembly_files"
DIR_OBJETOS="object_files"
DIR_EXECUTAVEIS="executables"

# Cria os diretórios, se ainda não existirem
mkdir -p "$DIR_ASSEMBLY"
mkdir -p "$DIR_OBJETOS"
mkdir -p "$DIR_EXECUTAVEIS"

# Caminhos completos para os arquivos
ARQUIVO_ASSEMBLY_PATH="$DIR_ASSEMBLY/$ARQUIVO_ASSEMBLY"
ARQUIVO_OBJETO_PATH="$DIR_OBJETOS/${ARQUIVO_ASSEMBLY%.s}.o"
ARQUIVO_EXECUTAVEL_PATH="$DIR_EXECUTAVEIS/$ARQUIVO_EXECUTAVEL"

# Gera o arquivo assembly
echo "Gerando o arquivo assembly..."
python3 main.py "$ARQUIVO_ENTRADA" > "$ARQUIVO_ASSEMBLY_PATH"
if [ $? -ne 0 ]; then
    echo "Erro ao gerar o arquivo assembly."
    exit 1
fi

# Gera o arquivo objeto
echo "Gerando o arquivo objeto..."
as --64 -o "$ARQUIVO_OBJETO_PATH" "$ARQUIVO_ASSEMBLY_PATH"
if [ $? -ne 0 ]; then
    echo "Erro ao gerar o arquivo objeto."
    exit 1
fi

# Gera o executável
echo "Gerando o arquivo executável..."
ld -o "$ARQUIVO_EXECUTAVEL_PATH" "$ARQUIVO_OBJETO_PATH"
if [ $? -ne 0 ]; then
    echo "Erro ao gerar o arquivo executável."
    exit 1
fi

echo "Compilação concluída com sucesso!"
echo "Executável gerado: $ARQUIVO_EXECUTAVEL_PATH"
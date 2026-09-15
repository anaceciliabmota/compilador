# Atividade 4 - Compiladores

O projeto recebe um arquivo como entrada com uma expressão de costantes, e é responsável por separar em tokens e estruturar como uma árore de expressões. Por fim, o programa retorna um código assembly

## Como rodar

Siga os passos abaixo para compilar e executar o programa:

1. **Usar o script `build.sh`**  
   O script `build.sh` automatiza as etapas de geração do arquivo assembly, do arquivo objeto e do executável. Para utilizá-lo, execute o comando abaixo, substituindo `<arquivo_de_entrada>`, `<arquivo_assembly_saida.s>` e `<nome_do_executavel>` pelos nomes apropriados:
   ```bash
   ./build.sh <arquivo_de_entrada> <arquivo_assembly_saida.s> <nome_do_executavel>
   ```
   Exemplo:
   ```bash
   ./build.sh test_files/teste1 teste1.s teste1
   ```

   Após a execução, os arquivos gerados serão organizados nas seguintes pastas:
   - **assembly_files/**: Contém os arquivos `.s` (código assembly).
   - **object_files/**: Contém os arquivos `.o` (arquivos objeto).
   - **executables/**: Contém os arquivos executáveis gerados.

2. **Executar o programa**  
   Após a geração do executável, você pode executá-lo diretamente da pasta `executables`:
   ```bash
   ./executables/<nome_do_executavel>
    ```
    Exemplo
    ```bash
   ./executables/teste1
   ```

3. **Testes**
   - Os testes para expressões com parenteses obrigatórios (Expressões Constantes 1) se encontram na pasta [test_files_ec1](test_files_ec1)
   - Os testes para expressões com parenteses obrigatórios (Expressões Constantes 2) se encontram na pasta [test_files_ec2](test_files_ec2)

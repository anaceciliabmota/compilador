# Compilador Fun — Atividade 4

A linguagem Fun estende a linguagem Cmd com suporte a **declaração e chamada de funções**, variáveis locais, parâmetros, recursão direta, escopo léxico, **tipagem estática**, **operadores lógicos** e novas **operações aritméticas**.

## Estrutura do Projeto

```
atividade4/
├── main.py              # Pipeline principal do compilador
├── tokens.py            # Tipos de token, lexer e classes de erro
├── syntax.py            # Nós da AST (Exp, Cmd, Declaracao, Programa, ...)
├── utils.py             # Parser (análise sintática) e análise semântica
├── codegen.py           # Geração de código assembly x86-64
├── runtime.s            # Runtime assembly (impressão do resultado e saída)
├── test_files_fun/      # Arquivos de teste para a linguagem Fun
├── test_files_cmd/      # Arquivos de teste para a linguagem Cmd (legado)
├── test_extensoes/      # Novos arquivos de teste das extensões implementadas
├── assembly_files/      # Assembly gerado (.s)
├── object_files/        # Arquivos objeto (.o)
└── executables/         # Binários gerados
```

## A Linguagem Fun

Um programa Fun é uma sequência de declarações de variáveis globais e funções, seguida de um bloco `main`:

```
var a: int = 9;
var b: int = 2;

fun abs(x: int) -> int {
    var y: int = 0;
    if x < 0 {
        y = 0 - x;
    } else {
        y = x;
    }
    return y;
}

main {
    return abs(a) + abs(b);
}
```

### Declarações

- `var <nome>: <tipo> = <exp>;` — declara e inicializa uma variável global ou local
- `fun <nome>(<params>) -> <tipo> { <vardecls> <cmds> }` — declara uma função. A lista de `<params>` utiliza o padrão `<nome>: <tipo>`.
- O sistema possui suporte explícito e verificação de tipos para os dados: `int` (Inteiros) e `bool` (Booleanos).

### Comandos

- `if <exp> { ... } else { ... }` — condicional (o `else` é obrigatório)
- `while <exp> { ... }` — repetição
- `<var> = <exp>;` — atribuição (apenas variáveis já declaradas)
- `return <exp>;` — retorna um valor da função a partir de qualquer ponto (o fluxo lógico e a pilha são encerrados neste ponto de forma segura)

### Expressões

- Constantes numéricas inteiras
- Constantes lógicas formais (`true` e `false`)
- Referências a variáveis
- Chamadas de função: `f(arg1, arg2, ...)`
- Operadores aritméticos nativos e avançados: `+`, `-`, `*`, `/`, `%` (Resto) e `^` (Exponenciação)
- Operadores relacionais: `<`, `>`, `==`
- Operadores lógicos: `all` (AND), `any` (OR) e o unário `not` (NOT)
- Agrupamento com parênteses

### Palavras-chave

`if`, `else`, `while`, `return`, `fun`, `var`, `main`, `int`, `bool`, `true`, `false`, `all`, `any`, `not`

### Comentários

Linhas iniciadas com `#`

## Como Usar

```bash
python3 main.py test_files_fun/<arquivo>
```

O compilador executa as fases em sequência:

1. **Análise léxica** — tokeniza o arquivo de entrada; detecta erros léxicos
2. **Análise sintática** — constrói a AST conforme a gramática de Fun
3. **Análise semântica** — verifica escopo lexo, chamadas e realiza a forte Verificação de Tipos.
4. **Geração de código** — produz o arquivo `.s` em `assembly_files/`
5. **Montagem** com `as` — gera o `.o` em `object_files/` (Exige Unix, MinGW ou WSL)
6. **Linkagem** com `ld` — gera o executável em `executables/` (Exige Unix, MinGW ou WSL)

Para rodar o binário gerado (se montado com sucesso):

```bash
./executables/<arquivo>
```

## Convenções de Chamada

O compilador usa a pilha para passagem de parâmetros e variáveis locais:

- Argumentos são empilhados em **ordem inversa** (último primeiro) antes do `call`
- O resultado da função é retornado em **RAX**
- No início de cada função: salva RBP, aloca espaço para vars locais (`sub $N, %rsp`), copia RSP para RBP
- Variáveis locais e parâmetros são acessados via deslocamento relativo a RBP
- Ao retornar em qualquer comando `return`: libera espaço das vars locais (se houver), restaura RBP, executa `ret`

## Arquivos de Teste

### Testes válidos (`test_extensoes/`)

| Arquivo | Descrição |
|---|---|
| `teste_extensoes` | Código consolidativo testando Resto(%), Múltiplos returns antecipados em IFs e Operadores Lógicos Booleanos puros |
| `exemplo_logico` | Loop/Branchs checando o uso amplo de 'all', 'any' e 'not' |

### Testes de erro semântico (`test_files_fun/` e `test_extensoes/`)

| Arquivo | Erro esperado |
|---|---|
| `erro_var_como_funcao` | Variável usada como função |
| `erro_funcao_como_var` | Função usada como variável em expressão |
| `erro_nome_funcao` | Variáveis não declaradas usadas como argumentos |
| `erro_semantico` | Chamada com aridade incorreta |
| `exemplo_tipagem_falha` | Verificação de conflito entre variável 'int' recebendo 'bool' barrada |

## Limitações

- Números negativos não são suportados diretamente na sintaxe (usar `0 - n`)
- Símbolos clássicos (`&&`, `||`) não existem, opte por sua versão natural em inglês (`all`, `any`)
- Funções mutuamente recursivas não são suportadas (apenas recursão direta)

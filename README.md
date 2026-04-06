# Compilador Fun — Atividade 4

A linguagem Fun estende a linguagem Cmd com suporte a **declaração e chamada de funções**, variáveis locais, parâmetros, recursão direta e escopo léxico.

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
├── assembly_files/      # Assembly gerado (.s)
├── object_files/        # Arquivos objeto (.o)
└── executables/         # Binários gerados
```

## A Linguagem Fun

Um programa Fun é uma sequência de declarações de variáveis globais e funções, seguida de um bloco `main`:

```
var a = 9;
var b = 2;

fun abs(x) {
    var y = 0;
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

- `var <nome> = <exp>;` — declara e inicializa uma variável global
- `fun <nome>(<params>) { <vardecls> <cmds> return <exp>; }` — declara uma função

### Comandos

- `if <exp> { ... } else { ... }` — condicional (o `else` é obrigatório)
- `while <exp> { ... }` — repetição
- `<var> = <exp>;` — atribuição (apenas variáveis já declaradas)

### Expressões

- Constantes numéricas inteiras
- Referências a variáveis
- Chamadas de função: `f(arg1, arg2, ...)`
- Operadores aritméticos: `+`, `-`, `*`, `/`
- Operadores relacionais: `<`, `>`, `==`
- Agrupamento com parênteses

### Palavras-chave

`if`, `else`, `while`, `return`, `fun`, `var`, `main`

### Comentários

Linhas iniciadas com `#`

## Como Usar

```bash
python3 main.py test_files_fun/<arquivo>
```

O compilador executa as fases em sequência:

1. **Análise léxica** — tokeniza o arquivo de entrada; detecta erros léxicos
2. **Análise sintática** — constrói a AST conforme a gramática de Fun
3. **Análise semântica** — verifica variáveis declaradas, diferencia escopo local/global, valida chamadas de função (existência e aridade)
4. **Geração de código** — produz o arquivo `.s` em `assembly_files/`
5. **Montagem** com `as` — gera o `.o` em `object_files/`
6. **Linkagem** com `ld` — gera o executável em `executables/`

Para rodar o binário gerado:

```bash
./executables/<arquivo>
```

## Convenções de Chamada

O compilador usa a pilha para passagem de parâmetros e variáveis locais:

- Argumentos são empilhados em **ordem inversa** (último primeiro) antes do `call`
- O resultado da função é retornado em **RAX**
- No início de cada função: salva RBP, aloca espaço para vars locais (`sub $N, %rsp`), copia RSP para RBP
- Variáveis locais e parâmetros são acessados via deslocamento relativo a RBP
- Ao retornar: libera espaço das vars locais, restaura RBP, executa `ret`

## Arquivos de Teste

### Testes válidos (`test_files_fun/`)

| Arquivo | Descrição | Resultado esperado |
|---|---|---|
| `teste1` | Função `abs` com `if/else`, chamada no `main` | valor absoluto |
| `teste_fib` | Fibonacci recursivo | `fib(10)` |
| `teste_sombra` | Parâmetro `x` oculta variável global `x` | 1 |

### Testes de erro semântico (`test_files_fun/`)

| Arquivo | Erro esperado |
|---|---|
| `erro_var_como_funcao` | Variável usada como função |
| `erro_funcao_como_var` | Função usada como variável em expressão |
| `erro_nome_funcao` | Variáveis não declaradas usadas como argumentos |
| `erro_semantico` | Chamada com aridade incorreta |

## Limitações

- Números negativos não são suportados diretamente na sintaxe (usar `0 - n`)
- Operadores lógicos (`&&`, `||`) não são suportados
- Funções mutuamente recursivas não são suportadas (apenas recursão direta)

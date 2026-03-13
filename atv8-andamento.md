# Atividade 8 – Andamento do Projeto

## O que foi feito

A partir do documento disponibilizado pelo professor, eis o que foi implementado até então.

### Alterações léxicas

- **Ponto-e-vírgula (`;`)** – Token `SEMICOLON`, usado para separar declarações.
- **Sinal de igual (`=`)** – Token `EQUAL` (Assignment), usado em atribuições (`identificador = expressão`).
- **Identificadores** – Token `IDENTIFIER`: sequência que começa com letra e pode ser seguida de letras ou dígitos (reconhecida em `scan_tokens` e classificada em `tipo_token`).

Arquivo: `utils.py` — enum `TipoToken`, função `tipo_token`, função `scan_tokens`.

---

### Alterações na sintaxe

O compilador passou a definir um **programa** formado por:

1. **Declarações** – linhas no formato `identificador = expressão;` (uma ou mais).
2. **Expressão final** – última linha no formato `= expressão` (sem identificador à esquerda).

As expressões continuam sendo constantes, operadores binários e parênteses; agora também podem conter **identificadores** (que serão variáveis, quando a semântica/geração de código for implementada).

---

### Função `programa`

**Onde:** `utils.py`.

**Assinatura:** `programa(tokens: List[Token]) -> (Programa, pos)`.

**Comportamento:**

- Inicia em `pos = 0`.
- Enquanto o token atual for `IDENTIFIER`, chama `decl(tokens, pos)` para obter uma `Declaracao` e avança; após cada declaração espera `SEMICOLON` e avança.
- Quando o token não é mais `IDENTIFIER`, espera `EQUAL` (início da expressão final).
- Chama `exp_a(tokens, pos+1)` para analisar a expressão final.
- Retorna `Programa(declaracoes, exp_final)` e a posição após a expressão final.

Ou seja: **programa = lista de declarações + expressão final**.

---

### Função `decl`

**Onde:** `utils.py`.

**Assinatura:** `decl(tokens: List[Token], pos: int) -> (Declaracao, pos)`.

**Comportamento:**

- O token em `pos` deve ser `IDENTIFIER` (nome da variável).
- Avança e exige token `EQUAL`.
- Avança e chama `exp_a(tokens, pos)` para obter a expressão da atribuição.
- Retorna `Declaracao(nome, exp)` e a posição após a expressão.

Formato esperado: `identificador = expressão` (o `;` é consumido em `programa`).

---

### Função `prim`

**Alteração:** além de **número** e **( expressão )**, passou a aceitar **identificador** como átomo.

- Se o token é `NUMERO` → retorna `Const(lexema)`.
- Se o token é `IDENTIFIER` → retorna `Identificador(lexema)` (nova classe).
- Se o token é `PARENTESE_ESQUERDO` → chama `exp_a` e exige `PARENTESE_DIREITO`.
- Caso contrário → levanta `ErroSintatico`.

Assim, identificadores podem aparecer em qualquer lugar onde uma expressão é esperada (por enquanto só na árvore; avaliação/geração de código para variáveis ainda não foi feita).

---

### Classes criadas

| Classe | Arquivo | Descrição |
|--------|---------|-----------|
| **`Programa`** | `utils.py` | Representa o programa inteiro: `declaracoes: List[Declaracao]` e `exp_final: Exp`. |
| **`Declaracao`** | `utils.py` | Uma linha `identificador = expressão`. Atributos: `nome: str`, `exp: Exp`.  |
| **`Identificador`** | `utils.py` | Subclasse de `Exp`. Representa o uso de um identificador (variável) dentro de uma expressão. Atributo: `nome: str`. |

---

## Uso no fluxo atual

- Em `main.py`, após a análise léxica e verificação de erros, chama-se `programa(tokens)` e imprime-se o objeto `Programa` retornado.
- A geração de código (assembly) e a avaliação ainda usam apenas `Const` e `OpBin`; **identificadores e declarações ainda não são tratados** na tradução nem na execução.

---

## Como rodar

```bash
python3 main.py <arquivo_entrada>
```

Exemplo de entrada válida:

```
x = (1 + 2);
y = (3 * 4);
= (x + y)
```

O programa atual imprime o objeto `Programa` com a lista de declarações e a expressão final.

## Pastas de teste

A pasta **`test_files_ev`** contém os arquivos de teste para esta atividade (expressões com variáveis / declarações).


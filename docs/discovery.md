# Discovery do Codebase: <PROJECT_NAME>

> **MODELO A PREENCHER.** Este arquivo vem vazio no kit. Quem preenche é o projeto: o processo `integrar` (ou o time, na etapa de discovery do `start-workflow`) troca os marcadores `<...>` e `(preencha: ...)` pelo que encontrar no código.
> Serve de snapshot do codebase para os subagentes, para que nenhum precise refazer a varredura. Complementa a referência do projeto em `.claude/PROJECT_REFERENCE.md` (gerada a partir de `templates/project-reference.template.md`).
> Para uma feature específica, copie este modelo e preencha só o que a feature usa.

- **Data da varredura:** <AAAA-MM-DD>
- **Escopo:** (preencha: projeto inteiro ou feature `<feature>`)

---

## 1. Arquivos essenciais do projeto

| Arquivo (caminho completo) | Papel |
| -------------------------- | ----- |
| `<APP_DIR>/<caminho>`      | (preencha: ex: definição de rotas, menu lateral, guards, configuração de ambiente) |

## 2. Estrutura de rotas ou pontos de entrada

(preencha: como a aplicação é iniciada e como as rotas, comandos ou endpoints são registrados)

```
<trecho relevante extraído do código>
```

## 3. Padrão de módulo de referência

- **Módulo usado como referência:** `<APP_DIR>/<caminho-do-modulo>`
- **Camadas e pastas:** (preencha: ex: domain, infra, main, view)
- **Convenções de nome:** (preencha: arquivos, classes, seletores)

```
<árvore de pastas do módulo de referência>
```

## 4. Componentes e utilitários compartilhados

| Item | Caminho | Quando usar |
| ---- | ------- | ----------- |
| (preencha) | `<APP_DIR>/<caminho>` | (preencha) |

## 5. Tratamento de erros e mensagens

(preencha: onde fica o tratamento de erros, como as mensagens chegam ao usuário e um trecho de exemplo de uso)

## 6. Autenticação e permissões

(preencha: como o login funciona, como as rotas são protegidas e o padrão de nome das permissões)

## 7. Testes e dados de teste

- **Unitários:** (preencha: framework, pasta, comando `<TEST_CMD>`)
- **E2E:** (preencha: framework, pasta `<e2e-dir>`, comando `<E2E_CMD>`; convenções em `docs/e2e.md`)
- **Mocks e fixtures:** (preencha: onde ficam e quais regras de validação os dados precisam respeitar)

## 8. Comandos do dia a dia

| Ação      | Comando           |
| --------- | ----------------- |
| Lint      | `<LINT_CMD>`      |
| Typecheck | `<TYPECHECK_CMD>` |
| Testes    | `<TEST_CMD>`      |
| Build     | `<BUILD_CMD>`     |

## 9. Pontos de atenção

- (preencha: código morto, partes frágeis, arquivos que não devem ser alterados, limitações conhecidas)

# Internacionalização do Symbiote-AI (`i18n/`)

O **Symbiote-AI** segue uma política **Brazil-first**: **`pt-BR`** é o idioma principal e canônico do kit (`README.md`, `processes/`, `templates/`, `adapters/`, `GUIA-DE-EXPANSAO.md`). Ao mesmo tempo, o repositório oferece documentação de entrada e referência em outros idiomas (começando por **English**) sem duplicar a lógica de processo nem introduzir drift silencioso.

## Por que `processes/*.md` permanece apenas em `pt-BR`

- **Fonte única de verdade sem drift:** duplicar dezenas de procedimentos canônicos em múltiplos idiomas criaria divergências de regras e custos altos de manutenção.
- **Execução multilíngue nativa:** os agentes de IA modernos leem os processos canônicos em `pt-BR` e produzem código, textos de UI, documentação, revisões e mensagens de commit no **idioma configurado para o projeto host** (definido via `simbiose` em `.claude/PROJECT_REFERENCE.md` e `AGENTS.md`).
- **Isolamento do kit:** `i18n/` fica na raiz do repositório do kit (assim como `adapters/`) e não precisa ser copiado para projetos host durante a instalação do `simbiose`.

## Estrutura e manifesto (`i18n/i18n.json`)

```text
README.md                 ← README canônico (pt-BR) com seletor de idioma
README.en.md              ← README em inglês com seletor de idioma
i18n/
├── i18n.json             ← manifesto declarativo (idioma canônico, locales e pares source → target)
├── README.md             ← este guia
└── en/
    ├── expansion-guide.md ← versão em inglês de GUIA-DE-EXPANSAO.md
    └── adapters.md        ← versão em inglês de adapters/README.md
```

## Idiomas disponíveis

| Código | Idioma | README | Guias traduzidos |
| --- | --- | --- | --- |
| `pt-BR` *(canônico)* | Português (Brasil) | [`README.md`](../README.md) | [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md), [`adapters/README.md`](../adapters/README.md) |
| `en` | English | [`README.en.md`](../README.en.md) | [`i18n/en/expansion-guide.md`](en/expansion-guide.md), [`i18n/en/adapters.md`](en/adapters.md) |

## Como adicionar um novo idioma (ex.: `es`)

1. Crie `README.<codigo>.md` na raiz traduzindo [`README.md`](../README.md) com a mesma estrutura de seções (`## `) e seletor de idioma apontando de volta para `README.md`.
2. Adicione o link de `README.<codigo>.md` no seletor de idioma no topo de [`README.md`](../README.md).
3. Crie `i18n/<codigo>/` com as traduções dos guias de entrada mantendo a mesma estrutura de seções (`## `) dos documentos canônicos em `pt-BR`.
4. Registre o novo idioma e seus pares `source` → `target` em [`i18n/i18n.json`](i18n.json).
5. Rode a validação local (também executada no CI) para verificar links, seletor bidirecional e paridade estrutural:

```bash
python3 -B scripts/validate-kit.py
python3 -B -m unittest discover -s tests -v
```

> Veja também a **Receita H** em [`GUIA-DE-EXPANSAO.md`](../GUIA-DE-EXPANSAO.md) (ou em [`i18n/en/expansion-guide.md`](en/expansion-guide.md)).

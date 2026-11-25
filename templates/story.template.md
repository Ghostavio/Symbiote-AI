# Story / Task: <título> (<tracker-id>)

> **Task com contexto embutido.** Template inspirado no *story-file* do [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) e no **Princípio 7** do `start-workflow`: reúne TUDO que um subagente precisa para implementar **sem abrir outros arquivos**. Preencha e **cole este conteúdo no prompt do subagente** (não passe só um caminho + linhas).

## Objetivo
<1-2 frases: o que entregar e por quê>

## Contexto (auto-contido — cole o TEXTO, não links)
- **Requisito(s):** <trecho relevante da spec/requisitos>
- **Design/decisões:** <trechos do design que afetam esta task>
- **Arquivos a criar/editar:** <lista com caminhos>
- **Padrões a seguir:** <convenções/exemplos do projeto — ex.: `templates/project-reference.template.md`>
- **Contratos/Tipos:** <DTOs, endpoints, assinaturas relevantes>
- **Tipo da task:** [ ] implementação pura  [ ] integração (depende de outra fase — Princípio 8)

## Critérios de aceite
- [ ] <critério 1 — testável>
- [ ] <critério 2>

## Testes
- <quais testes criar (unitário/E2E)>
- **Dados de mock/fixtures DEVEM passar nos validadores do projeto** (CPF, CNPJ, email…) — Princípio 9.

## Fora de escopo
- <o que NÃO fazer nesta task>

## Verificação (ordem — Princípio 10)
- [ ] lint  · [ ] typecheck  · [ ] testes  · [ ] code review (`phase-code-review`)

## Modelo sugerido para o subagente
<Sonnet (mecânico) | Opus (complexo/crítico) — ver Passo 1.5 do start-workflow>

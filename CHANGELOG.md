# Changelog

Todas as mudanças relevantes do **Symbiote-AI** são registradas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.2.0] — 2026-11-27

### Adicionado
- **Identidade Symbiote-AI:** adoção do novo nome e identidade visual em [`docs/brand/symbiote-ai.png`](docs/brand/symbiote-ai.png) (#6).
- **Entrada unificada `simbiose`:** `simbiose` passou a ser a entrada única para aplicar o kit em projetos existentes ou iniciar projetos novos, com detecção de contexto, confirmação em casos ambíguos e compatibilidade preservada para os comandos depreciados `integrar` e `scaffold` (#7, #13, #15).
- **Suporte nativo de primeira classe para Antigravity e Gemini CLI:** nova camada aberta `.agents/skills/<name>/SKILL.md`, ponto de entrada enxuto `GEMINI.md` e documentação de transporte Streamable HTTP `/mcp` vs. `mcp-remote` em `ai-tools-matrix.md` (#9).
- **Arquitetura de adaptadores composíveis (`adapters/`):** contrato declarativo em `adapters/README.md` (`adapter.json`, `files.conventions`, `files.review_checks`, e opcionais `files.editor_settings`/`files.skills`) organizado em `stacks/`, `cloud/` e `observability/`, com primeiro adaptador-piloto completo em `adapters/stacks/angular/`, proteção contra symlinks/path traversal e detecção de colisões de skills antes da escrita (#16).
- **Validador, CI e testes automatizados:** [`scripts/validate-kit.py`](scripts/validate-kit.py), workflow CI em Linux e macOS (`.github/workflows/ci.yml`) e suíte `tests/` cobrindo paridade de wrappers/aliases, links, scripts shell, adaptadores e time tracking (#4, #5, #16, #17).
- **Esforço configurável e combinação de modelos:** suporte a níveis `low` / `medium` / `high` / `max` (precedência tarefa → sessão → projeto → `medium`) e estratégia combinada de implementação + revisão em `processes/start-workflow.md` (#12).

### Alterado
- **Core neutro de stack:** removido o acoplamento residual de Angular, Vitest, `angular-schematics` e `tslint` dos entry points (`AGENTS.md`, `.github/copilot-instructions.md`, `.cursor/settings.json`) e dos processos canônicos (`phase-code-review`, `start-workflow`, `full-setup`, `integrar`), preservando as práticas Angular no adaptador `adapters/stacks/angular/` (#11, #16).
- **Fluxo Express sem atrito:** adaptado para rodar localmente sem credenciais, MCPs ou setup global, escolhendo porte pelo risco e reversibilidade (#10).
- **Revisão de código proporcional ao risco:** separação clara entre *Avaliação* (preserva arquivos, commits e registros externos) e *Revisão de implementação* (correções focadas no escopo autorizado), priorizando análise estática local (`eslint-plugin-sonarjs` / linters nativos) e mantendo SonarQube como complemento opcional (#8, #12).
- **Time tracking neutro de provedor:** consolidação em `processes/timesync.md` com guardrails contra deleção/duplicação automática de worklogs e Tempo Timesheets como candidato para times Jira (#4).

### Corrigido
- **Semântica de fuso horário em 7pace e Clockify:** novo helper [`scripts/time-entry-interval.py`](scripts/time-entry-interval.py) valida timestamps ISO 8601 com fuso explícito (`Z` ou `±HH:MM`), calcula duração em UTC sem depender do `date` do sistema operacional e normaliza os envios para UTC (`Z`), usando `timeStamp` no 7pace e `git log --format=%aI` no diário (#17).
- **Confiabilidade dos scripts de time tracking:** propagação de falhas HTTP no Clockify (#2) e simulação `--dry-run` do 7pace sem credenciais no `/bin/bash` nativo do macOS (#5).
- **Consistência estrutural do kit:** correção de links quebrados e validação cruzada de `alias_of` entre ferramentas (#4, #7).

## [0.1.0] — 2026-11-26

### Adicionado
- Baseline público inicial do kit (então *AI Workflow Kit*) com processos canônicos, wrappers para Claude Code, Cursor, Codex e Copilot, templates e scripts de time tracking para iniciar o ciclo de auto-aprimoramento.

[0.2.0]: https://github.com/Ghostavio/Symbiote-AI/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Ghostavio/Symbiote-AI/releases/tag/v0.1.0

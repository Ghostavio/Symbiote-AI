# Symbiote-AI

![Identidade visual do Symbiote-AI. Ferrofluido preto envolve um núcleo facetado, e os espaços entre os dois sugerem um S na versão plana.](docs/brand/symbiote-ai.png)

O Symbiote-AI se integra a projetos novos ou existentes e amplia o que a equipe já faz com desenvolvimento assistido por IA. O kit oferece processos portáteis para iniciar trabalho, levantar requisitos, escrever especificações, revisar código, sincronizar horas e acompanhar tarefas no board. Funciona nativamente com **Claude Code**, **Antigravity**, **Gemini CLI**, **Codex**, **Cursor** e **VSCode + Copilot**.

> Extraído e generalizado de um workflow real de um time de produto. O core é **neutro de stack**, os dados específicos de projeto usam **placeholders** (`<...>`) e especializações por tecnologia vivem como **adaptadores opcionais** em [`adapters/`](adapters/README.md).

## Filosofia (por que isto é portátil)

- **Processos canônicos tool-neutral** em [`processes/`](processes/) — a fonte de verdade, independente de ferramenta.
- **Wrappers finos por ferramenta** que só apontam para os canônicos:
  - Antigravity / Gemini CLI / Codex → `.agents/skills/<name>/SKILL.md` + `AGENTS.md` / `GEMINI.md`
  - Claude Code → `.claude/skills/<name>/SKILL.md`
  - Cursor → `.cursor/rules/<name>.mdc`
  - VSCode + Copilot → `.github/copilot-instructions.md`
- **`ai-tools-matrix.md`** mapeia os nomes de tool-call de MCP entre as ferramentas.
- **Adaptadores opcionais** em [`adapters/`](adapters/README.md) isolam especializações de stack (`angular`, `react`), cloud (`cloudflare`, `aws`) e observabilidade (`opentelemetry`) fora do core neutro, acoplados seletivamente pela skill `simbiose`.
- **Placeholders** (`<AZURE_ORG>`, `<PROJECT_KEY>`, `<TEST_CMD>`, …) marcam tudo que é específico de projeto. A skill `simbiose` os preenche.

Trocar de ferramenta ou de tracker = editar wrappers/matrix, sem tocar nos processos.

## Começando

Com o kit disponível na ferramenta de IA, invoque a skill **`simbiose`** (ex.: **`$simbiose`** no Codex, **`/simbiose`** no Claude Code, ou peça *"Use a skill simbiose"* no Antigravity e no Gemini CLI — no Gemini CLI, use `/skills list` para conferir se ela foi descoberta). Se estiver trabalhando em outro diretório, informe o caminho de destino. A skill detecta um projeto existente e propõe a adaptação (incluindo adaptadores compatíveis em `adapters/`), ou prepara a criação de um projeto novo. Quando o contexto for ambíguo, ela pergunta antes de começar.

Para disponibilizar as skills diretamente em um repositório existente, copie o conteúdo do kit para a raiz desse repositório, preservando os arquivos de configuração existentes.

**Depois, em qualquer caso:**
1. Preencha os `.env` a partir dos `.env.example` (no kit: `.claude/integrations/timetracking/.env.example`, usado pelo Clockify) (NUNCA versione segredos).
2. Configure as integrações que o projeto usa, como `setup-azure-mcp` ou `setup-jira` para o tracker e `setup-7pace` para registrar horas. Use `setup-sonarqube-mcp` se o projeto já tiver uma instância SonarQube.
3. (Opcional) Rode `full-setup` para instalar ferramentas de sistema e plugins.
4. Comece a trabalhar com `start-workflow` (use o **Fluxo Express** para mudanças pequenas).

## Skills

| Skill | O que faz |
|---|---|
| `simbiose` | Aplica o kit a um projeto existente ou cria um projeto novo já integrado |
| `start-workflow` | Ponto de entrada de uma sessão: Feature, Bug, Follow-up, Refatoração, Testes, **Express**, Freestyle |
| `figma-requirements` | Levanta requisitos a partir de um design no **Figma** (MCP local ou online) |
| `spec-builder` | Constrói a especificação de uma feature a partir do template |
| `create-work-item` | Cria/vincula work item no tracker (Azure DevOps / Jira) |
| `phase-code-review` | Code review com análise e testes proporcionais ao risco, com correções quando autorizadas |
| `timesync` | Registra horas em uma ou mais ferramentas de controle de tempo configuradas no projeto |
| `docs-target` | Define se a doc vai pro repo ou pra plataforma externa (Confluence/Outline/Notion) |
| `setup-azure-mcp` / `setup-jira` | Configura o MCP do tracker (Azure DevOps ou Jira/Atlassian) |
| `setup-sonarqube-mcp` | Configura o MCP do SonarQube (via Docker) |
| `setup-7pace` | Configura a integração com 7pace |
| `full-setup` | Setup completo do ambiente numa máquina nova |

## Layout

```
Symbiote-AI/
├── README.md                     ← este arquivo
├── CHANGELOG.md                  ← histórico de versões e releases
├── LICENSE                       ← texto da Apache License 2.0
├── NOTICE                        ← aviso de copyright e licença
├── .gitignore                    ← deixa os .env fora do git (mantém os .env.example)
├── GUIA-DE-EXPANSAO.md           ← como trocar ferramentas e criar skills ou adaptadores
├── ai-tools-matrix.md            ← mapeamento de tool-calls por ferramenta de IA
├── AGENTS.md                     ← catálogo e instruções para Codex / Antigravity / Gemini CLI
├── GEMINI.md                     ← ponto de entrada enxuto para Gemini CLI / Antigravity
├── .agents/
│   └── skills/<skill>/SKILL.md   ← padrão aberto Agent Skills (Antigravity, Gemini CLI, Codex)
├── .github/
│   ├── copilot-instructions.md   ← wrapper VSCode + Copilot
│   └── workflows/ci.yml          ← validação automática em Linux e macOS
├── .claude/                      ← Claude Code: skills, integrações, settings
│   ├── PROJECT_REFERENCE.md      ← referência do projeto (modelo a preencher)
│   ├── settings.json             ← permissões
│   ├── skills/<skill>/SKILL.md
│   └── integrations/
│       ├── timetracking/         ← wrapper 7pace+Clockify (com .env.example, sem .env)
│       └── clockify-mcp/         ← (opcional, não vem no kit) criada pelo git clone do MCP do Clockify
├── .cursor/
│   ├── settings.json             ← preferências mínimas do editor (formatação/lint ficam a cargo do projeto)
│   └── rules/<skill>.mdc         ← wrappers Cursor (+ PROJECT-REFERENCE-md.mdc)
├── processes/                    ← PROCESSOS CANÔNICOS (fonte de verdade)
├── adapters/                     ← adaptadores opcionais (stacks/angular, stacks/react, cloud/cloudflare, cloud/aws, observability/opentelemetry)
├── templates/                    ← spec-template, story.template, project-reference (template)
├── docs/                         ← workflow, discovery (modelo a preencher), e2e, processo-work-items, aprendizados
├── scripts/                      ← validador (`validate-kit.py`) e timesync (`time-entry-interval.py`, `sync-7pace.sh`, `setup-7pace.*`)
└── tests/                        ← testes automatizados do validador, adaptadores e scripts de timesync
```

## Ferramentas e integrações

- **Ferramentas de IA:** suporte nativo para **Claude Code**, **Antigravity**, **Gemini CLI**, **Codex**, **Cursor** e **VSCode + Copilot** (via wrappers + `ai-tools-matrix.md`). Outras ferramentas entram pela Receita E do `GUIA-DE-EXPANSAO.md`.
- **Tracker:** Azure DevOps **ou** Jira/Atlassian (`setup-jira`).
- **Qualidade:** análise estática local, como [SonarJS via ESLint](https://github.com/SonarSource/SonarJS/blob/master/packages/analysis/src/jsts/rules/README.md) em JS/TS, com SonarQube via MCP quando já configurado.
- **Time tracking:** 7pace e Clockify (timestamps ISO 8601 com fuso explícito normalizados para UTC), adaptável a **Toggl/Harvest** conforme as instruções do `GUIA-DE-EXPANSAO.md`.
- **Documentação:** no repo **ou** externa (Confluence/Outline/Notion) via `docs-target` — para PRs limpos.
- **Design:** Figma via MCP (local Dev Mode ou hospedado) na `figma-requirements`.
- **Browser/visual:** Playwright MCP (validação visual e E2E).
- **Superpowers** (https://github.com/obra/superpowers): pacote multi-plataforma de skills de processo (brainstorming, TDD, debugging, code review) usado pelos canônicos.

## Validação local

Para validar paridade de wrappers, links internos, scripts shell, adaptadores e testes unitários:

```bash
python3 -B scripts/validate-kit.py
python3 -B -m unittest discover -s tests -v
```

## Segurança

- **Nenhum segredo** vai no kit. Tokens vêm de variáveis de ambiente / secret managers; os `.env` ficam fora do pacote — use os `.env.example`.
- O kit não traz hook de segredos. Se quiser bloquear a leitura de arquivos com segredos detectados, instale o hook do CLI da SonarSource no seu projeto (ver *Componentes opcionais de terceiros*).
- Os scripts de timesync leem o token de env vars (preferindo Keychain/1Password/Bitwarden — ver `setup-7pace`).

## Princípios

O kit embute lições de desenvolvimento assistido por IA "agressivo" — ver [`docs/aprendizados.md`](docs/aprendizados.md) e a seção *Princípios* em [`processes/start-workflow.md`](processes/start-workflow.md). Resumo: editar docs via orquestrador; esforço configurável (`low`/`medium`/`high`/`max`) e combinação de modelos por complexidade; revisão proporcional ao risco, com correções autorizadas; isolar execuções/revisões concorrentes nos mesmos arquivos; verificações rápidas antes de suítes longas; porte do fluxo conforme risco e escopo; tracker e diário proporcionais à entrega.

## Expandindo

Para trocar Azure DevOps por Jira, 7pace por Toggl, repo por Confluence, adicionar uma nova ferramenta de IA ou criar um novo adaptador de stack/cloud/observabilidade: ver [`GUIA-DE-EXPANSAO.md`](GUIA-DE-EXPANSAO.md) e [`adapters/README.md`](adapters/README.md). A skill `simbiose` automatiza a maior parte dessas escolhas.

## Metodologias relacionadas (prior art)

Este kit é uma síntese leve e neutra de ferramenta. Ele se inspira em — e combina bem com — métodos maiores:

- **[Superpowers](https://github.com/obra/superpowers)** — pacote multi-plataforma de skills de processo (brainstorming, TDD, debugging, planning, code review). Os processos canônicos invocam `superpowers:*` diretamente.
- **[BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)** (MIT) — framework agêntico de dev ágil com planejamento *scale-adaptive* e agentes especializados. O kit já incorpora seus pilares: porte de fluxo por complexidade (Express vs Completo + roteamento de esforço/modelo) e **task com contexto embutido** ([`templates/story.template.md`](templates/story.template.md), inspirado no *story-file* do BMAD). Combinação útil: faça o planejamento pesado nas *web bundles* do BMAD (Gemini/ChatGPT) e traga os artefatos para o `spec-builder`.
- **Spec-workflow (kfc)**: fluxo de spec orientado a documentos (requirements, design, tasks), com subagentes da extensão Kiro for Claude Code. Não vem no kit; ver *Componentes opcionais de terceiros*.

> O kit reúne procedimentos em Markdown, adaptadores opcionais e scripts, adaptáveis via `simbiose`. Ver também [`CHANGELOG.md`](CHANGELOG.md).

## Componentes opcionais de terceiros (não incluídos)

Estes componentes não vêm no kit, porque têm licença própria. Instale à parte se quiser usá-los:

- **Kiro for Claude Code** (https://github.com/notdp/kiro-for-cc), licença AGPL-3.0: traz os agentes de spec "kfc" e o fluxo de spec orientado a documentos.
- **Hook de segredos do CLI da SonarSource** (https://github.com/SonarSource/sonarqube-cli), licença LGPL-3.0: bloqueia a leitura de arquivos com segredos detectados. Para ter o hook, rode no seu projeto o comando de integração do CLI `sonar` (ver a documentação do repositório).

## Licença

Apache License 2.0. Ver [`LICENSE`](LICENSE) e [`NOTICE`](NOTICE).


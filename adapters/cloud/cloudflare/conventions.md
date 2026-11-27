# Adaptador de Cloud — Cloudflare

Convenções recomendadas para projetos executados na plataforma **Cloudflare** (Workers, Pages, KV, D1, R2, Durable Objects, Queues e Hyperdrive) acoplados ao **Symbiote-AI**. Ao aplicar este adaptador via `simbiose`, incorpore apenas os serviços realmente usados no projeto host e registre os comandos locais confirmados no `.claude/PROJECT_REFERENCE.md`.

## Runtime de borda e ciclo de vida de Workers

- **Compatibilidade com o runtime V8 isolado:** prefira Web Standard APIs (`fetch`, `Request`, `Response`, `Web Crypto`, `Streams`). Só utilize APIs do Node.js quando `nodejs_compat` e a `compatibility_date` estiverem explicitamente configurados no manifesto Wrangler.
- **Trabalho em segundo plano com `ctx.waitUntil(...)`:** toda operação assíncrona executada após montar a resposta (logs, telemetria, invalidação de cache, envio de evento) deve ser registrada em `ctx.waitUntil(...)` — promessas soltas podem ser canceladas imediatamente ao encerrar a requisição.
- **Sem estado mutável por usuário em escopo global:** isolados podem ser reutilizados entre requisições distintas; nunca armazene dados de sessão, tokens ou contexto de requisição em variáveis globais de módulo.
- **Limites operacionais:** respeite limites de tempo de CPU, memória, tamanho de bundle e número de subrequests por invocação; use streaming em vez de carregar payloads grandes inteiros em memória.

## Bindings, configuração e segredos

- **Tipagem de `Env` e bindings explícitos:** declare bindings (`KV`, `D1`, `R2`, `DO`, `Queues`, `Service Bindings`) em `wrangler.toml`/`wrangler.jsonc` e mantenha a interface `Env` sincronizada (ex.: tipos gerados pelo projeto).
- **Separação de ambientes:** isole configurações de `dev`/`staging`/`production` com namespaces, bancos e buckets distintos — nunca aponte ambiente local ou preview para recursos de produção.
- **Segredos fora do Git:** nunca grave tokens, chaves privadas ou senhas em `[vars]` do arquivo Wrangler. Use Cloudflare Secrets (`wrangler secret` / secret store) em produção e `.dev.vars` (listado no `.gitignore`) para desenvolvimento local.

## Armazenamento, mensageria e consistência

- **KV:** indicado para leitura intensa e baixa latência com **consistência eventual**; não use para contadores exatos, locks distribuídos ou transações críticas.
- **D1 (SQLite na borda):** use sempre queries parametrizadas (`.bind(...)`), migrations versionadas e índices compatíveis com o padrão de leitura; evite concatenação de SQL.
- **R2 (Object Storage):** valide `Content-Type`, tamanho máximo e chaves/prefixos antes de gravar; use URLs pré-assinadas ou validação de autorização explícita para objetos privados.
- **Durable Objects:** use quando precisar de coordenação fortemente consistente ou estado serializado por entidade/chave, mantendo o escopo de cada objeto pequeno para evitar gargalos de concorrência.
- **Queues:** trate consumidores como *at-least-once* — implemente processamento **idempotente**, limite tamanho de batch, configure retries/DLQ e faça `ack()`/`retry()` por mensagem quando aplicável.

## Cache de borda e segurança

- **Cache consciente:** defina `Cache-Control` e uso da Cache API explicitamente; nunca armazene respostas autenticadas, personalizadas ou com PII em cache público compartilhado (valide `Vary` e bypass para cookies/headers de autenticação).
- **Fronteira de entrada:** valide payload, cabeçalhos, assinaturas de webhook (em tempo constante via Web Crypto) e política CORS estrita.

## Testes e verificações locais

- **Isolamento da lógica:** separe regras de domínio do handler `fetch`/`queue`/`scheduled` para permitir testes unitários rápidos e portáteis.
- **Testes com bindings locais:** quando o projeto usar Miniflare ou `@cloudflare/vitest-pool-workers` (ou outro runner configurado), valide bindings e migrations localmente.
- **Comandos confirmados:** preencha os comandos reais no `.claude/PROJECT_REFERENCE.md` apenas com scripts e binários instalados no host (evite `npx` sem `--no-install`). Em revisões automatizadas, restrinja-se a verificações locais/não destrutivas (nunca execute deploy em produção sem aprovação explícita).

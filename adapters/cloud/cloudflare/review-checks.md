# Review Checks — Adaptador Cloudflare

Checklist especializado para carregar em [`processes/phase-code-review.md`](../../../processes/phase-code-review.md) (§2, §3, §4 e §7–§8) quando o adaptador `cloudflare` estiver acoplado ao projeto.

## §2 Code Quality & Patterns (Cloudflare)

- [ ] Bindings utilizados no código existem no arquivo Wrangler (`wrangler.toml`/`wrangler.json`/`wrangler.jsonc`) e estão refletidos na tipagem `Env` (quando o projeto usa TypeScript).
- [ ] Trabalho assíncrono pós-resposta (telemetria, auditoria, invalidação de cache) está envolvido em `ctx.waitUntil(...)` com tratamento de erro.
- [ ] APIs específicas do Node.js só são usadas quando `nodejs_compat` está declarado no manifesto Wrangler.
- [ ] Queries em D1 utilizam parâmetros vinculados (`.bind(...)`) sem concatenação direta de strings SQL.
- [ ] Regras de negócio estão desacopladas dos handlers `fetch`/`queue`/`scheduled`, facilitando testes unitários.

## §3 Architecture & Layer Consistency (Cloudflare)

- [ ] Escolha do primitivo coerente com o requisito de consistência (KV para leitura eventual, D1 para relacional, Durable Objects para coordenação forte, R2 para objetos, Queues para trabalho assíncrono).
- [ ] Ambientes (`dev`/`staging`/`production`) utilizam recursos isolados (IDs de KV, D1, buckets R2 e filas distintos).
- [ ] Migrations de D1 (quando houver) estão versionadas e backward-compatible com o rollout planejado.

## §4 Bug Detection & Security (Cloudflare)

- [ ] **Vazamento de segredos:** nenhuma chave, token ou senha em `[vars]` do `wrangler.*` ou em código versionado; `.dev.vars` protegido pelo `.gitignore`.
- [ ] **Vazamento cross-request:** nenhum estado mutável específico de usuário ou requisição armazenado em variável global de módulo entre invocações do mesmo isolado.
- [ ] **Cache poisoning / exposição de dados:** nenhuma resposta autenticada, privada ou com PII sendo gravada em cache público da borda sem chave/bypass seguro.
- [ ] **Idempotência e filas:** consumidores de Queues lidam com reentrega (*at-least-once*), falhas parciais (`ack`/`retry`) e DLQ sem duplicar efeitos colaterais.
- [ ] **Limites de runtime:** sem buffering integral de payloads grandes em memória (usar streams) e sem fan-out descontrolado de subrequests em loops.

## §7–§8 Quality Checks (exemplos condicionais Cloudflare)

Execute **apenas** os scripts e ferramentas realmente instalados e confirmados no projeto host (`.claude/PROJECT_REFERENCE.md` / `package.json`). Evite `npx` sem `--no-install` e **nunca** execute deploys reais (`wrangler deploy`) sem autorização explícita do usuário.

Exemplos condicionais (somente locais e não destrutivos, quando configurados no projeto):

```bash
npm test                                               # testes unitários / Miniflare / vitest-pool-workers configurados
npm run typecheck                                      # somente se TypeScript estiver configurado no host
./node_modules/.bin/wrangler deploy --dry-run          # validação local do bundle/config, somente se Wrangler estiver instalado
```

# Review Checks — Adaptador OpenTelemetry

Checklist especializado para carregar em [`processes/phase-code-review.md`](../../../processes/phase-code-review.md) (§2, §3, §4 e §7–§8) quando o adaptador `opentelemetry` estiver acoplado ao projeto.

## §2 Code Quality & Patterns (Observabilidade)

- [ ] Logs de produção utilizam o logger estruturado do projeto (sem `console.log`/`print` soltos) com nível adequado e campos semânticos consistentes.
- [ ] Spans manuais sempre têm encerramento garantido (`span.end()` em `try/finally` — inclusive dentro de `startActiveSpan` em JS/TS —, `with` em Python, `defer span.End()` em Go ou wrapper equivalente que efetivamente encerre o span) e registram falhas com `recordException` + status `ERROR`.
- [ ] Nomes de spans e métricas seguem convenções semânticas OpenTelemetry com nomenclatura estável e parametrizada (ex.: `GET /orders/:id`).
- [ ] Logs emitidos durante requisições/jobs preservam correlação com `trace_id`/`span_id` quando há contexto ativo.

## §3 Architecture & Layer Consistency (Observabilidade)

- [ ] Inicialização do SDK e exportadores OTLP fica isolada no bootstrap/infraestrutura (sem acoplar regras de domínio puras a SDKs proprietários).
- [ ] Propagação de contexto W3C (`traceparent`/`tracestate`) preservada ao atravessar fronteiras assíncronas (HTTP, gRPC, filas, background jobs).
- [ ] Endpoints OTLP, headers de autenticação e taxas de sampling vêm de configuração/env vars, nunca hardcoded no código.

## §4 Bug Detection, Security & Cost (Observabilidade)

- [ ] **Explosão de cardinalidade:** nenhum ID dinâmico (`user_id`, `order_id`, UUID), e-mail, timestamp ou URL crua usado como label/atributo de métrica ou nome de span.
- [ ] **Vazamento de PII e segredos:** nenhum header `Authorization`/`Cookie`, token, senha, dado pessoal sensível ou payload bruto sendo gravado em logs ou atributos de span.
- [ ] **Vazamento de spans / perda de telemetria:** ausência de spans abertos sem `end()` em retornos antecipados ou blocos `catch`; processos efêmeros/serverless fazem `forceFlush()`/`shutdown()` adequadamente.
- [ ] **Ruído e custo:** sem logging excessivo dentro de loops quentes ou retries sem backoff, e sem re-logar o mesmo erro/stack trace em múltiplas camadas.

## §7–§8 Quality Checks (exemplos condicionais Observabilidade)

Execute **apenas** os scripts e ferramentas realmente instalados e confirmados no projeto host (`.claude/PROJECT_REFERENCE.md`), evitando invocar ferramentas não instaladas via `npx` ou coletar/enviar telemetria para backends de produção durante testes locais.

Exemplos condicionais (somente quando a respectiva ferramenta/configuração existir no projeto):

```bash
# Rodar testes de instrumentação configurados no projeto (ex.: com InMemorySpanExporter / exporter mockado)
# Validar sintaxe de configuração do OpenTelemetry Collector quando o binário existir localmente:
otelcol --config=otel-collector-config.yaml validate

# Em projetos Kubernetes com kubectl e contexto confirmados (somente leitura, sem -f/--follow):
kubectl config current-context
kubectl logs -n <namespace> <pod> -c <container> --since=15m --tail=200 --timestamps
kubectl logs -n <namespace> <pod> -c <container> --previous --tail=200
```

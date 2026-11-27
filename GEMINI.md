# Symbiote-AI — Gemini / Antigravity Entry Point

Siga as convenções do projeto e o catálogo completo de processos em [`AGENTS.md`](AGENTS.md).

- **Descoberta progressiva de skills:** todas as skills do kit estão expostas no padrão aberto em `.agents/skills/<name>/SKILL.md` (descobertas automaticamente pelo **Antigravity** e pelo **Gemini CLI** via `/skills`), apontando para os procedimentos canônicos em [`processes/`](processes/).
- **MCP, subagentes e equivalências:** consulte [`ai-tools-matrix.md`](ai-tools-matrix.md) (no Antigravity, `~/.gemini/config/mcp_config.json` usa **Stdio** ou **Streamable HTTP** `/mcp`; endpoints SSE legados exigem bridge como `mcp-remote`).

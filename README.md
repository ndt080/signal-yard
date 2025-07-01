# 🚦 SignalYard — AI-ready Platform for Railway Diagnostics and Docs

**SignalYard** is a modular system that connects multiple MCP servers to provide unified access to signal history, technical documentation, and AI-powered diagnostics via a lightweight LLM interface.

---

## 📚 Key Features

- 🧠 **LLM Gateway** — Smart assistant that analyzes input and returns potential equipment issues, causes, and resolutions with links to documentation.
- 🛠 **Signal Archive** — MCP server storing and serving historical data of binary signals and equipment states.
- 📄 **DocsHub** — Static documentation server containing industry standards, equipment manuals, and internal instructions.
- 🔀 **Modular Architecture** — Easy to extend with additional MCP servers or custom modules.
- 🚧 **Railway-Focused** — Designed specifically for railway diagnostics, fault tracing, and maintenance workflows.


## 🧱 Architecture

```text
        ┌────────────────────┐
        │     LLM Gateway    │ ◄────────────┐
        └────────┬───────────┘              │
                 │                          │
 ┌───────────────┼────────────────────────┐ │
 ▼               ▼                        ▼ ▼
┌────────────┐ ┌────────────────┐ ┌────────────┐
│ Signal MCP │ │ Docs MCP       │ │ Future MCP │ ...
└────────────┘ └────────────────┘ └────────────┘
 (Signals DB)   (Documentation)     (Extensible)
```

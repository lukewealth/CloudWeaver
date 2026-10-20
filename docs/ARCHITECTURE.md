# CloudWeaver — System Architecture

## 1. High-Level View

CloudWeaver is a multi-agent system for cloud operations decision support.  
Four specialised agents operate under a central orchestrator that enforces consensus before any significant action is taken.

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard                         │
│              (status, decisions, agent health)              │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / JSON
┌──────────────────────────▼──────────────────────────────────┐
│                     FastAPI Layer                           │
│                  (routers, auth surface)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 Agent Orchestrator                          │
│   • Message router                                          │
│   • Decision objects + voting                               │
│   • Lifecycle management (start / stop / status)            │
└──────┬──────────┬──────────┬──────────┬─────────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Cost    │ │ Security │ │  Auto    │ │ Incident │
│ Optimizer│ │ Auditor  │ │  Scaler  │ │Responder │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                        │
              Cloud SDKs / LLM APIs / IaC concepts
```

## 2. Core Abstractions

### AgentMessage
Signed inter-agent communication unit. Carries sender, receiver, content, timestamp, and optional signature for future MPC-style verification.

### AgentDecision
First-class decision object:

- `action_type`
- `target_resource`
- `proposed_changes`
- `estimated_impact`
- `risk_score`
- `votes` (agent → bool)

Consensus is currently majority (`> 0.5`). This design makes agreement **observable** and easy to reason about in interviews.

## 3. Agent Contracts

Each agent is expected to support:

- `initialize()`
- `run()` (long-running async loop)
- `stop()`
- `get_status()`
- `evaluate_decision(decision) → bool`
- `execute(decision)` (only after consensus)
- `receive_message(msg)`

This uniform interface allows the orchestrator to treat agents as interchangeable participants in the consensus process.

## 4. Consensus Flow

1. Any component (or agent) can propose an `AgentDecision`.
2. Orchestrator broadcasts the decision to all agents.
3. Each agent returns a vote via `evaluate_decision`.
4. If majority approval is reached, the orchestrator routes execution to the responsible agent.
5. Execution is logged; side effects are intentionally limited in the current prototype.

## 5. Design Principles

| Principle | Implementation |
|-----------|----------------|
| Separation of concerns | One responsibility per agent |
| Observability of decisions | Explicit Decision + votes objects |
| Safe-by-default | Vote before execute |
| Interview clarity | Small, readable modules with clear contracts |
| Extensibility | New agents only need to implement the common interface |

## 6. Future Extensions (Roadmap)

- Real tool-calling / function calling against cloud APIs
- Structured evaluation harness (cost of proposals, false-positive rate of security findings, etc.)
- Persistent decision log + audit trail
- Authentication / multi-tenant isolation on the API layer
- Richer frontend visualisations of agent reasoning traces

## 7. How to Discuss This in Interviews

Recommended framing:

> “CloudWeaver is a multi-agent cloud-ops prototype. I focused on clean agent boundaries, an explicit consensus mechanism, and a FastAPI + React surface so the system is both runnable and discussable. The current implementation prioritises architectural clarity over full production hardening.”

Be ready to walk through:

- Why specialised agents beat a single mega-prompt
- How the voting / decision object works
- What would be required to move from prototype to production (observability, auth, rate limits, human-in-the-loop gates, evaluation metrics)

# BFT Progress Council MCP

> ## 🧱 Part of the MEOK A2A Substrate
>
> Run all 12 A2A primitives + this BFT council as one signed pipeline for
> **£499/mo** (100K calls), or pay **£0.0002/call**. See
> [meok.ai/a2a](https://meok.ai/a2a).

# Anti-loop guardrail for AI agents

<!-- mcp-name: io.github.CSOAI-ORG/bft-progress-council-mcp -->

[![PyPI](https://img.shields.io/pypi/v/bft-progress-council-mcp)](https://pypi.org/project/bft-progress-council-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-Published-green)](https://registry.modelcontextprotocol.io)

> ## 💰 Stops your agent burning tokens on loops
>
> Every agentic coding tool — Cursor, Claude Code, Devin, Aider — bleeds tokens
> when the agent gets stuck and keeps retrying. This MCP runs a **5-voter
> Byzantine Fault Tolerant council** that halts the loop the moment 3 of 5 voters
> agree there's no real progress.
>
> Typical save: **£10-£200 per agent run** depending on agent + task length.
> Pays for the £29/mo Starter tier the first time it halts a stuck loop.

## The problem

You're running an agent (Cursor / Claude Code / Aider / Devin / a custom MCP
orchestration). It hits a tricky bug. Or a missing dependency. Or a 403 from
an API. Instead of stopping, it just keeps **trying**. Different prompts, same
fundamental error. Each retry costs API tokens. By the time you check, it's
spent £50.

Sound familiar? That's because every existing agentic loop has one weakness:
**it doesn't know whether it's making progress**. It only knows whether the
last action succeeded. So when it can't tell the difference between "trying
harder" and "spinning", it just keeps spinning.

## The solution

Five independent voters look at the last N actions + the original goal and
each return a verdict. We tally. If 3 of 5 say PROGRESS, continue. If 3 of 5
say STALL / DRIFT / BLOCKED, **halt**.

| Voter | Detects |
|---|---|
| `repetition` | Literal action repetition in last 5 actions |
| `outcome_diversity` | Identical outcomes / repeated error strings (429, 403, exception messages) |
| `goal_alignment` | Drift from the original goal (token overlap) |
| `action_velocity` | Rapid-fire spinning with no human-loop pause |
| `artefact_growth` | No tangible artefacts being produced (no writes / commits / deploys) |

Free tier uses the deterministic heuristic voters (above). **Pro tier** swaps
them for 5 actual LLM voters (Claude Opus + GPT-5 + Gemini 2.5 + Llama 3.3 +
Step 3.6) which catch subtler stalls.

## Quick install

```bash
# uvx (preferred — no install)
uvx bft-progress-council-mcp

# pip
pip install bft-progress-council-mcp

# npx (via @meok-ai bridge)
npx @meok-ai/bft-progress-council-mcp
```

Add to your Claude Desktop / Cursor / Windsurf MCP config:

```json
{
  "mcpServers": {
    "bft-progress-council": {
      "command": "uvx",
      "args": ["bft-progress-council-mcp"]
    }
  }
}
```

## Usage

Three tools to call from your agent loop:

```python
# 1. Start a session at the top of your agent run
{"tool": "start_session", "args": {"goal": "Fix the EU AI Act Article 50 watermarking bug in src/article50.py"}}
# → { session_id: "s_1779...", goal: "...", started_at: "..." }

# 2. Record every action you take
{"tool": "record_action", "args": {
    "session_id": "s_1779...",
    "action": "Edit src/article50.py: add C2PA manifest validation",
    "outcome": "Test still failing on missing-key.png"
}}

# 3. Periodically (every 5-10 actions) — let the council vote
{"tool": "council_vote", "args": {"session_id": "s_1779...", "lookback": 10}}
# → {
#     "verdict": "STALL",
#     "action_recommended": "halt_loop_and_request_new_approach",
#     "tally": {"PROGRESS": 1, "STALL": 3, "DRIFT": 0, "BLOCKED": 1},
#     "votes": [
#       {"voter": "repetition", "verdict": "STALL", "reason": "only 2 unique actions in last 5"},
#       {"voter": "outcome_diversity", "verdict": "BLOCKED", "reason": "4 of 5 outcomes contain 'failing'"},
#       {"voter": "goal_alignment", "verdict": "PROGRESS", "reason": "60% goal-token overlap"},
#       {"voter": "action_velocity", "verdict": "STALL", "reason": "rapid-fire actions (1.2s avg)"},
#       {"voter": "artefact_growth", "verdict": "STALL", "reason": "no commits in last 10"}
#     ],
#     "signed_attestation": { ... HMAC-SHA256 signed ... }
# }
```

When the verdict is anything other than PROGRESS, the agent **stops** and either
re-anchors to the original goal or escalates to the human. No more silent
overnight loops eating tokens.

## The maths

Free tier saves you tokens. Here's the simple cost model:

- Avg agent step: ~2,000 tokens (input + output blended)
- Claude Opus 4.7 blended cost: ~£0.025 per 1K tokens
- Each prevented "wasted action loop" averages 5+ extra steps
- One halt = 5 × 2,000 × £0.025/1K = **~£0.25 saved per halt**
- A typical multi-hour agent run hits 4-12 stall events
- Per-run saving: **£1-£3 in tokens**

That's just the free tier. Substrate customers running fleets of agents save
**£100-£1,000/month** with one MCP. £29/mo Starter pays for itself in hours.

Verify your own ROI with the `estimate_tokens_saved` tool — pass the session
ID and it'll calculate the cost saved given your halt history.

## Tiers

| Tier | Price | What |
|---|---|---|
| **Free** | £0 (MIT) | Heuristic voters, local-only attestations, self-host |
| **Starter** | £29/mo | Managed signing key + verify.meok.ai attestation, 10K sessions/mo |
| **Pro** | £79/mo | 5 actual LLM voters (Claude + GPT + Gemini + Llama + Step), 100K sessions, 24h SLA |
| **A2A Substrate** | £499/mo | This + 11 other A2A MCPs (handoff, audit-logger, policy, firewall, etc.) |
| **Universe** | £1,499/mo | All 48 MEOK MCPs · 500K calls |
| **Defence** | £4,990/mo | Pro + on-prem + dedicated CSM |

Buy: https://meok.ai/a2a · https://buy.stripe.com/bJe3cx6WgcMO38142k8k90o

## Sister MCPs

Part of the MEOK **A2A** pack:

- **Prompt Injection Firewall** → `uvx agent-prompt-injection-firewall-mcp`
- **Audit Logger** → `uvx agent-audit-logger-mcp`
- **Policy Enforcement** → `uvx agent-policy-enforcement-mcp`
- **Rate Limiter** → `uvx agent-rate-limiter-mcp`
- **Certified Handoff** → `uvx agent-handoff-certified-mcp`
- **Identity + Trust** → `uvx agent-identity-trust-mcp`

Full catalogue + Anthropic Registry verify links: [meok.ai/anthropic-registry](https://meok.ai/anthropic-registry)

## Protocol coverage + Universal PAYG

- ✅ **MCP** (Anthropic) — native
- ✅ **A2A** (Google + Linux Foundation, absorbed IBM ACP)
- ✅ **IBM ACP** — covered via A2A merge
- ◐ **Stripe ACP** (Agentic Commerce) — Q3 bridge
- ◐ **AP2** (Google Agent Payments) — partial
- ◐ **x402** (Coinbase HTTP 402) — via api.meok.ai gateway
- → **OASF / AGNTCY** — Q3 bridge

| Option | Price | Best for |
|---|---|---|
| Self-host (this MCP) | £0 — MIT | Devs |
| This MCP Starter | £29/mo | One-MCP teams |
| Universal PAYG | £29/mo + £0.0002/call | Spiky usage |
| A2A Substrate | £499/mo | A whole pack |
| Universe | £1,499/mo | All 48 MCPs |

## Why this matters for MEOK

Every other MEOK MCP makes you *do* something. This one tells you *when to
stop*. It's the cheapest insurance policy in the catalogue — and it sits
alongside the agent-rate-limiter and agent-audit-logger as the third
guardrail in the A2A Substrate.

## Licence

MIT. By [MEOK AI Labs](https://meok.ai) (CSOAI LTD, UK Companies House
16939677). Founder: [Nicholas Templeman](mailto:nicholas@meok.ai).

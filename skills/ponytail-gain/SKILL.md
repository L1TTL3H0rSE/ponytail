---
name: ponytail-gain
description: >
  Show ponytail's measured impact as a compact scoreboard: less code, fewer
  tokens, lower cost, and faster completion from the current agentic benchmark.
  One-shot display, not a persistent mode, and not a per-repo number. Trigger:
  /ponytail-gain, "ponytail gain", "what does ponytail save", "show ponytail
  impact", "ponytail scoreboard".
---

# Ponytail Gain

Display this scoreboard when invoked. One-shot: do NOT change mode, write flag
files, or persist anything.

Use the current published agentic benchmark from the README and
`benchmarks/results/2026-06-18-agentic.md`: 12 feature tasks on a real
FastAPI + React repository, Haiku 4.5, n=4. The figures are measured against
the same agent without ponytail; they are not computed from the current repo.

## Scoreboard

Render this compact scoreboard:

```
  ponytail gain                    agentic benchmark · 12 tasks · Haiku 4.5

  Lines of code   no-skill  100%   ponytail  46%   ▼ 54%
  Tokens          no-skill  100%   ponytail  78%   ▼ 22%
  Cost            no-skill  100%   ponytail  80%   ▼ 20%
  Time            no-skill  100%   ponytail  73%   ▼ 27%
  Safety          no-skill  100%   ponytail 100%   =

  This repo:  /ponytail-debt  (shortcuts you deferred)
              /ponytail-audit (what's still cuttable)
```

The older isolated-generation benchmark reached 80–94% fewer lines on some
single-shot tasks, but do not present that range as the general headline. The
agentic benchmark above is the current defensible baseline.

## Honesty boundary

These are benchmark results, not this repo. NEVER print a per-repo savings
number ("you saved X lines/tokens here"): the unbuilt version was never
written, so there is no real baseline to subtract from in a live repo. The
only real per-repo figures come from `/ponytail-debt` (a counted ledger), and
this card points there instead of inventing one.

## Boundaries

One-shot display. Edits nothing, changes no mode.
"stop ponytail" or "normal mode": revert.

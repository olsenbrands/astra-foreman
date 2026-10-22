# Model reference — dated evidence 2026-10-22

These facts are supplied by the shared model-refresh spec dated 2026-10-22;
this offline update did not re-query providers. They are evidence examples,
not pinned routing rules or proof of account access. Prices are standard API
USD per million input/output tokens, not subscription charges or measured usage.
Resolve each needed line to its newest visible version with
`scripts/resolve_models.py`; confirm with one cheap ping before the first real
dispatch. On an unknown/not-entitled refusal, record why and try the next-newest
visible version in that same line. See [routing.md](routing.md).

## Dated evidence, not dispatch candidates

| Line / dated model | API $/M input / output | Evidence on 2026-10-22 |
|---|---:|---|
| sol / `gpt-6.1-sol` | 2 / 10; cached input .10 | 1.05M context; AA Intelligence Index v4.3.2 52 at max, versus 48 for previous-generation `gpt-6-sol` |
| astra / `gpt-6-astra` — PREMIUM | 10 / 50 | II 53; GPT-6.1 Astra was announced then cancelled for safety; no automatic dispatch |
| luna / `gpt-6-luna` | .10 / .50 | No 6.1 luna in this dated catalog |
| opus alias / Opus 5.5 | 4 / 20 | II 58 at max |
| sonnet alias / Sonnet 5.5 | 2 / 10 | II 56 at max; released 2026-09-28 |
| haiku alias / Haiku 5.5 | .10 / .50 up to 100K prompt tokens; .50 / 2.50 above | II 29–43 by effort; released 2026-10-07 |
| fable alias / Fable 5.1 — PREMIUM | 10 / 50 | II 53; no automatic dispatch |
| Grok base / `grok-4.7` | 2 / 6 | 500K context; whole request 2× at 200K prompt tokens; 4.7 Fast is a 2×-priced variant |
| Jev latest alias / Jev 1.14 | .042 / 0 | Released 2026-10-14; served ID `typesafe/jev-1.14-20261014`; 32K/64K default limits, optional long-context header |

Do not choose `gpt-6-sol` while `gpt-6.1-sol` is available: the catalog labels
it "Previous generation", and the sol line has a newer visible successor.
Descriptions corroborate identity; numeric version comparison selects it.
Similarly, a future visible luna successor is used automatically, even though
this table predates it. Record "line <x> resolved to <id> (newer than evaluated
<id>)" and check access. Missing/malformed catalog data is not permission to
guess a default. A new line is "unknown line — recon first"; evaluate it in a
bounded recon pass before use. Grok suffixed variants are never the base default.

Premium is by line for all versions of astra and fable. The table supplies cost
evidence only; it grants no dispatch authority. The user must request the exact
premium route and then separately confirm the model and its cost in this same
session, as defined in [SKILL.md](../SKILL.md#premium-dispatch-requires-two-user-approvals).
An existing premium lead is fine. Never use Codex `ultra`: it automatically
delegates, including workers spawning workers.

Use the live runtime's supported effort and context limits. A published API
context ceiling does not override a smaller harness window. Claude's `opus`,
`sonnet`, and `haiku` aliases already track newest models. Jev's default is
`~typesafe/jev-latest`, with explicit pin fallbacks `typesafe/jev-1.14` then
`typesafe/jev-1.13`; read its response `model` and pin that served ID for the
rest of this session. See [jev.md](jev.md) for advisory-only use and privacy.

Tool charges, service tiers, cache behavior, context growth, retries and total
volume affect cost. Benchmarks are dated context, not task qualification.
A catalog listing or sign-in does not establish entitlement. An access ping
establishes that request works; only serving metadata establishes `SERVED`
identity. Do not convert API dollars into subscription quota.

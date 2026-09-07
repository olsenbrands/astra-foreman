# Routing and economics

## Make a decision, not a leaderboard

Choose among available, authorized model-and-tool combinations that meet the
task's capability, impact, context, and independence needs. Tool convenience
affects feasibility and cost, but must not silently exclude a suitable model or
provider family. Native Codex is a complete fallback, not the only normal candidate.
Compare expected total completion cost and quota pressure, not model price alone.
Include context setup, lead supervision, tools, expected repairs, and review.
For a difficult coupled task, a short frontier execution may cost less than
several cheaper attempts. When uncertainty is material, use the stronger plausible
seat or one bounded, reversible representative task before implementing. Comparable
accepted work is useful qualification evidence. Where experience is absent, treat
current model guidance as a tentative starting point; do not require a new
calibration exercise in every campaign or make prior acceptance a permanent bar.

## Cross-family review where it can change the decision

For a substantial plan, strongly prefer one qualified reviewer from a different
provider family before broad implementation when an authorized route is already
usable. Ask it to challenge the user-goal interpretation, missing outcomes,
architecture, high-impact assumptions, and proposed evidence of success. State
the question and the decision it could change. This is the planned architecture
review, not another gate or a review of every brainstorming exchange.

Substantial means the plan contains interacting components or decisions with
costly downstream consequences; file count does not decide it. For this routing
choice, OpenAI, Anthropic/Claude, and xAI/Grok are separate families; Astra and
Sol are both OpenAI. Use a qualified same-family reviewer when capability, access,
user preference or restriction, or expected total cost makes it the better route,
and briefly record why. Do not install a tool, buy access, create an account, or
wait for quota merely to satisfy family diversity. Codex-only operation remains
complete.

Use a cross-family implementation review selectively for high-impact boundaries
such as permissions, payments, data loss, installation or update behavior, and
process ownership; repeated missed criteria; or unresolved material disagreement.
Prefer substituting it for a planned review instead of adding a review. Try a
direct test first when it can settle the question cheaply. A disagreement alone
does not justify a third reviewer: the lead adjudicates the evidence and assigns
only unresolved consequential questions.

These are starting hypotheses for Astra or Sol leads, not measured rankings:

First apply [crew-control.md](crew-control.md). These are role candidates, not
required accounts. Use the same capability hierarchy within Codex alone.

| Work and residual judgment | Initial candidates | Effort starting point |
|---|---|---|
| Extract facts, enumerate callers, prescribed mechanical change | Luna; Haiku when its tools/pool fit better | Low on Luna; supported default on Haiku |
| Bounded recon that must interpret behavior | Terra, Sonnet, or Grok when its tools and context fit | Medium; high for interacting paths |
| Known-interface implementation, meaningful tests, coherent refactor | Qualified Terra, Sonnet, or Grok | Medium for routine logic; high for multi-step coding |
| Cheap additional hypotheses or competing design critique | Terra or Grok | Medium; substantiate claims before using them |
| Ordinary bounded change review | Qualified Terra, Sonnet, or Grok in a fresh context | Medium/high according to reasoning burden |
| Consequential plan or code review, hard debugging | Qualified frontier route such as Sol, Opus, or Grok in a fresh context | High; raise only for specific unresolved difficulty |
| Architecture, difficult integration, ambiguity, final acceptance | Current Astra or Sol lead | Current effort; request a higher supported level only if needed |

FAST is for low residual judgment, WORKHORSE for bounded decisions, FRONTIER for
unresolved design or difficult interaction. Apply impact separately: a prescribed
security-sensitive edit can use a workhorse builder but need frontier review.
No cheaper builder earns authority to certify its own work.

Do not require a permanent provider caste. Opus is a useful starting candidate
for consequential cross-family review, and another qualified route can serve when
its available model, tools, context, and independence clear the same task-specific
bar. Final acceptance always belongs to the lead. Benchmarks and vendor descriptions
are priors, not proof of reliability in this repository. Higher effort does not
automatically equal a more capable model and effort names do not transfer across
providers.

## Discover once; refresh on a reason

Inspect the current native spawn schema, model controls, effort choices, capacity,
and inherited-context behavior. For external routes, inspect installed CLI
version/help, sanitized auth status, and available model metadata. Do not print
credentials, whole config files, raw environment variables, or account identifiers.
CLI presence and login do not prove a particular model is entitled or served.

Cache this observation within the run. Refresh on model change, auth/routing
failure, relevant CLI update, unfamiliar model, or a stale fact that would alter
the next decision. Search current primary vendor documentation for unknown models
and pricing. Do not repeat model research before every ticket.

The native schema in the development session supported model/effort pins with a
fresh or limited context fork, but not with a full-history fork. Inspect the live
schema: never assume a task named `terra` runs Terra. Never silently inherit an
expensive lead for bulk labor when the economy depends on a smaller model.

Record requested model/effort separately from the evidence:

- `REQUESTED`: exact pin accepted by the invocation surface.
- `INHERITED_UNCONFIRMED`: no evidenced per-child pin or serving identity.
- `SERVED`: runtime/provider metadata explicitly identifies the serving model;
  record effort separately if exposed. Self-report is only a claim.
- `BILLED`: provider cost metadata, which does not establish serving identity.

A missing serving field is uncertainty, not a failed product test. Keep
task assurance and model provenance separate. If an exact model or cost class
is a user requirement, unresolved identity prevents claiming that requirement
passed. Otherwise inspect the work under the disclosed route uncertainty.
If serving metadata contradicts the requested route, stop further dispatch on
that route and resolve it before making class-dependent decisions.

## Effort and context

Use only the intersection of model support and the actual execution surface.
Do not translate a Codex `xhigh` setting into a Claude or Grok flag by analogy.
Haiku 4.5 does not expose the same effort parameter as adaptive-thinking Claude
models. Some Codex surfaces expose `ultra` while API guidance lists through `max`;
do not assume `ultra` has a particular orchestration meaning or spend it by default.

Pass original intent and criteria inline, and bounded source paths for detail.
Keep worker reports concise with links to raw proof. Reuse useful builder context
for related repairs; never use that warmed context for its independent verifier.
Sequential execution does not guarantee cross-session cache reuse.

## Cost evidence and adaptation

Default objective: minimize total expected usage across authorized providers while
preserving quality. Honor a different user priority, such as Codex endurance or
latency. Do not ask for a budget merely to do an ordinary small assignment.

For a sprint, state a qualitative or measured envelope before broad fan-out and
reserve capacity for review, repair, and closure. Record any user cap exactly.
Without spend telemetry, use bounded concurrent workers, short evidence checkpoints,
and an outcome-based stop/replan rule; do not claim a hard dollar cap is enforced.

Record per provider: billing mode, input, cached input, output/reasoning when
exposed, reported cost, elapsed time, retries, accepted outcomes, and lead usage
when available. Missing numbers are `unavailable`, never zero. API estimates
are not subscription charges or proven allowance-depletion rates. Do not sum
incompatible accounting fields or count reasoning twice when included in output.

At the first accepted outcome and each meaningful milestone, compare forecast
with observed total cost. If review/coordination dominates, consolidate boundaries
or make a bounded takeover only for a concrete cause; if repairs dominate, return
the routine repair to its builder first, improve the contract, or route upward.
Do not estimate the remaining program from one unrepresentative task as if certain.

Keep the written session crew record specified in [crew-control.md](crew-control.md).
Change defaults on repeated comparable evidence, not a model's self-rating or one
lucky pass. Do not update global memory or shared model policy without authority.

## Dated reference, verified 2026-09-05

Standard short-context API USD per million input/output tokens. These numbers
exclude cache handling, long-context premiums, tools, service tiers, and subscription
accounting. Refresh when they materially affect a choice.

| Model ID | Input / output | Source |
|---|---|---|
| `gpt-6-astra` | 10 / 50 | [OpenAI comparison](https://developers.openai.com/api/docs/models/compare) |
| `gpt-5.6-sol` | 4 / 20 | Same comparison |
| `gpt-5.6-terra` | 2 / 12 | Same comparison |
| `gpt-5.6-luna` | 0.20 / 1.20 | [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) |
| `claude-opus-5` | 5 / 25 | [Claude models](https://platform.claude.com/docs/en/models/overview) |
| `claude-sonnet-5` | 2 / 10 | Same overview |
| `claude-haiku-4-5-20251001` | 1 / 5 | Same overview |
| `grok-4.6` | 2 / 6 | [xAI pricing](https://docs.x.ai/developers/pricing) |

Grok's published long-context threshold is 200K with higher whole-request rates;
do not infer an individual call stayed below it from average tokens per turn.
Use per-call telemetry when available and include tool/context overhead. Smaller
fresh task context is preferable to blindly sending a whole sprint history.

Primary guidance: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model),
[Claude overview](https://platform.claude.com/docs/en/models/overview),
[Grok 4.6](https://docs.x.ai/developers/grok-4-6).
No public source here establishes which model is the best reviewer for this user's
projects. Validate the routing hypotheses with accepted work.

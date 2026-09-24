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

These are role hypotheses, not measured rankings. Apply
[crew-control.md](crew-control.md) first. The exact model, effort, tools, context,
transport and access must fit the task. [model-reference.md](model-reference.md)
records dated IDs, API economics and limits; refresh it when a decision depends
on current facts.

| Work and residual judgment | Initial candidates | Effort starting point |
|---|---|---|
| Fact extraction or prescribed mechanical change | `gpt-6-luna`; qualified Haiku | Low on Luna; supported default on Haiku |
| Bounded recon or coding with meaningful tests | `gpt-6-sol`; qualified Sonnet or `grok-4.7` | Medium, high for interacting paths |
| Coherent refactor, difficult implementation, hard debugging | `gpt-6-sol`; qualified `claude-opus-5-5`, `grok-4.7`, or Astra | High only for a specific reasoning need |
| Ordinary independent change review | Fresh qualified Sol, Sonnet, Grok, or other capable route | Match effort to impact and residual judgment |
| Consequential plan/code review | Fresh qualified `claude-opus-5-5`, Sol, Astra, or `grok-4.7` | High when warranted; separate reviewer context |
| Architecture, integration, ambiguity, final acceptance | Current Astra or Sol lead | Current effort, raised for a concrete difficulty |

FAST means the remaining work is extraction or a prescribed mechanical step
with cheap, direct verification. WORKHORSE means bounded decisions or coherent
coding with known interfaces and meaningful checks. FRONTIER means unresolved
design, coupled behavior, or a high-impact failure mode whose absence is hard to
prove. These are quality floors for the **task**, based on residual judgment and
risk; no model name grants a tier. Qualify the specific model, effort, tools,
context, access, and independent review route against that floor.

For consequential review, name the high-impact failure modes and the direct
evidence needed to test or reason about them. The reviewer must be able to
independently inspect that evidence and explain why each named risk is or is not
addressed. A familiar provider label or generic PASS is insufficient. If no
eligible authorized reviewer can do this, keep the outcome REVIEW PENDING;
do not silently move to a restricted premium pool.

Luna has an impact and judgment floor: do not give it an ambiguous implementation,
security-sensitive decision, or consequential review solely for its price. Sol is
a strong coding and agentic default and a valid lead, but its name does not
promote every Sol review to frontier assurance. A qualified Grok route may build
or review, including consequential work when its evidence, tools and independence
clear the same bar. Grok 4.6 is an optional output-light candidate only when
comparable local measurements favor its total token volume and accepted result.
It is not a universally superior or required substitute for 4.7. Preserve
qualified legacy routes such as `gpt-5.6-terra` when current models are
unavailable; `gpt-6-terra` was not in the verified current catalog. Final
acceptance belongs to the lead. A prescribed sensitive edit can have a workhorse
builder and a stronger independent review. Compare
accepted outcomes and whole-route cost, not model labels or vendor benchmarks.

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
models. The local Codex catalog currently describes `ultra` as automatic task delegation.
For a worker contract that forbids delegation, do not choose it unless the live
surface demonstrates bounded authorized behavior. The API effort list and native
runtime schema differ; use their actual intersection for this dispatch.

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

## Dated model facts

See [model-reference.md](model-reference.md), verified 2026-09-24, for exact IDs,
API prices, cache and long-context treatment, effort ranges, and current caveats.
API estimates do not measure subscription consumption. Use the live runtime
catalog for dispatch limits. A successful exact-model request proves that route
usable; only serving metadata establishes `SERVED`
identity. The published API context ceiling does not override a smaller runtime
window.

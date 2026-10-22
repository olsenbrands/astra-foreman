# Routing and economics

## Make a decision, not a leaderboard

Choose among available, authorized model-and-tool combinations that meet the
task's capability, impact, context, and independence needs. Tool convenience
affects feasibility and cost, but must not silently exclude a suitable model or
provider family. Native Codex is a complete fallback, not the only normal candidate.
Compare expected total completion cost and quota pressure, not model price alone.
Include context setup, lead supervision, tools, expected repairs, and review.
For a difficult coupled task, a short frontier execution (nonpremium unless the
premium rule is satisfied) may cost less than several cheaper attempts. When
uncertainty is material, use the stronger plausible nonpremium seat or one bounded,
reversible representative task before implementing. Comparable
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
| Fact extraction or prescribed mechanical change | `luna` line; qualified `haiku` alias | Low on Luna; supported default on Haiku |
| Bounded recon or coding with meaningful tests | `sol` line; qualified `sonnet` alias or Grok base line | Medium, high for interacting paths |
| Coherent refactor, difficult implementation, hard debugging | `sol` line; qualified `opus` alias or Grok base line | High only for a specific reasoning need |
| Ordinary independent change review | Fresh qualified `sol`, `sonnet`, or Grok base line | Match effort to impact and residual judgment |
| Consequential plan/code review | Fresh qualified `opus`, `sol`, or Grok base line | High when warranted; separate reviewer context |
| Architecture, integration, ambiguity, final acceptance | Current user-selected lead | Current effort, raised for a concrete difficulty |

FAST means the remaining work is extraction or a prescribed mechanical step
with cheap, direct verification. WORKHORSE means bounded decisions or coherent
coding with known interfaces and meaningful checks. FRONTIER (nonpremium unless
the premium rule is satisfied) means unresolved
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
promote every Sol review to frontier assurance (nonpremium unless the premium
rule is satisfied). A qualified Grok route may build
or review, including consequential work when its evidence, tools and independence
clear the same bar. Resolve Grok's highest visible numeric base version; never
choose an older base by habit or a suffixed variant as a default. A previously
used Codex line outside sol/luna/astra requires bounded recon before use, even
when a legacy route once worked. Terra is a known old line, reported as
known/superseded-or-unused and never used by routing. Final
acceptance belongs to the lead. A prescribed sensitive edit can have a workhorse
builder and a stronger nonpremium independent review. Compare
accepted outcomes and whole-route cost, not model labels or vendor benchmarks.

## Resolve lines, then confirm access

Every candidate above means the newest visible version of that line, never a
pinned historical ID. From the skill directory run:

```sh
python3 scripts/resolve_models.py --line sol --json
python3 scripts/resolve_models.py --line luna --catalog /path/models_cache.json --json
```

The resolver reads `${CODEX_HOME:-~/.codex}/models_cache.json` (`models` entries
with `slug`, `description`, `visibility`), requires `visibility: "list"`, ignores
hidden/nonmatching entries, and compares version components numerically: 6.10
beats 6.9. The local catalog checked on 2026-10-22 had visibility on all 9 entries;
missing or other visibility values are excluded. Its JSON `candidates` contain
`id` and `description`, ordered newest first. Corroborate the selection with the catalog's wording
("Latest", "Previous generation", "Older"). Do not pick `gpt-6-sol` now that
`gpt-6.1-sol` exists: it is explicitly previous generation, and the known sol
line has a newer visible successor. If discovery fails, reconcile the catalog
or choose another already-qualified nonpremium route; never guess a current ID.

A newer version in a known line is selected automatically. Record "line <x>
resolved to <id> (newer than evaluated <id>)". Before the first real dispatch,
confirm with one cheap access ping on the intended transport. If unknown/not
entitled, try the next-newest visible candidate **in the same line**, record the
refusal, and confirm that candidate before dispatch. Stop on policy refusals;
auth, quota, and transport failures use the availability rules, not blind version
cycling. Reuse successful access evidence within the session.

For Grok, read the signed-in provider catalog with `grok models`; copy the returned
IDs into the offline resolver (include variants; the resolver excludes them):

```sh
python3 scripts/resolve_models.py --provider grok --ids grok-4.6,grok-4.7,grok-4.7-build-fast --json
# --line grok --ids <comma-separated-provider-ids> is equivalent.
```

The IDs above are dated examples; use the provider's actual listing. It numerically selects
the highest `grok-<version>` and excludes every suffixed variant. Claude harness
aliases `opus`, `sonnet`, `haiku` track their newest versions. Jev resolves its
latest alias and records the served session pin as described in [jev.md](jev.md).

A new nonpremium Codex line is reported as "unknown line — recon first".
Premium variants remain premium, never recon-first. Do not promote a new line
to a default, fallback, or second opinion until bounded recon evaluates its
capability, cost, and access. A listing is never qualification or entitlement.

## Premium is excluded from automatic routing

All routing, fallback, escalation, recon, review, verifier, and second-opinion
choices are nonpremium. Codex `astra`, including suffixed variants, at **any
version**, and Claude fable alias /
claude-fable-* at **any version**, require the user's request followed by a second
confirmation in this same session naming the exact resolved model and cost.
Apply the [premium rule](../SKILL.md#premium-dispatch-requires-two-user-approvals)
before any call, including an access ping. Generic approval of a provider, a
review, a budget, or a prior session is insufficient. A premium lead is fine;
it does not grant permission to spawn premium children. Record both approvals
and refuse premium dispatch when either is absent. Do not offer premium as a
default or automatically escalate to it when a quality floor cannot be met.

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
schema: never assume a task named `terra` runs Terra. Under a premium lead,
a child without an explicit nonpremium model pin IS a premium dispatch.
Always pin an explicit nonpremium model (resolved newest `sol`/`luna`, or a
nonpremium Claude/Grok route) on every spawn; if the spawn schema cannot pin a
model, do not spawn — do the work inline or use a CLI route that pins it.
This includes a full-history fork that disallows a model pin.

Every CLI launch (`codex exec`, `claude -p` / `--print`, or `grok`), including
an access ping, must pass an explicit nonpremium `--model` flag. A launch relying
on the CLI's configured default is unconfirmed and possibly premium: the user's
Codex or Claude default could be Astra or Fable. Do not launch without the flag;
an explicitly pinned premium model requires both current-session approvals.

Record requested model/effort separately from the evidence:

- `REQUESTED`: exact pin accepted by the invocation surface.
- `INHERITED_UNCONFIRMED`: no evidenced per-child pin or serving identity.
  Under a premium lead this IS a premium dispatch, requiring both approvals;
  it never permits an unpinned spawn or bypasses the nonpremium-pin rule above.
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
Check the current Claude alias's supported effort controls rather than copying
settings from another model. Never use Codex `ultra`: it automatically delegates,
including workers spawning workers, and breaks bounded worker ownership. The API
effort list and native runtime schema differ; use their actual intersection.

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
the routine repair to its builder first, improve the contract, or route upward
within qualified nonpremium routes. Premium dispatch still requires both approvals.
Do not estimate the remaining program from one unrepresentative task as if certain.

Keep the written session crew record specified in [crew-control.md](crew-control.md).
Change defaults on repeated comparable evidence, not a model's self-rating or one
lucky pass. Do not update global memory or shared model policy without authority.

## Dated model facts

See [model-reference.md](model-reference.md), dated 2026-10-22, for exact IDs,
API prices, cache and long-context treatment, effort ranges, and current caveats.
API estimates do not measure subscription consumption. Use the live runtime
catalog for dispatch limits. A successful exact-model request proves that route
usable; only serving metadata establishes `SERVED`
identity. The published API context ceiling does not override a smaller runtime
window.

# Model reference — verified 2026-09-24

These are published **standard API** prices in USD per million tokens, not Codex
subscription charges, Claude allowance consumption, or a quality ranking. The
columns are input / cache read / cache write (5-minute; 1-hour where offered) / output. Tool charges, service tiers,
retries and context growth can change total cost. A fixed same-token estimate is
only an API illustration, not measured usage or a recommendation.

| Exact model ID | API $/M input / read / write / output | Published context | Role note |
|---|---:|---:|---|
| `gpt-6-astra` | 10 / 1 / 12.5 / 50 | 1,050,000 | Difficult judgment; qualified lead |
| `gpt-6-sol` | 2 / .2 / 2.5 / 10 | 1,050,000 | Coding and agentic work; qualified lead |
| `gpt-6-luna` | .1 / .01 / .125 / .5 | 1,050,000 | Mechanical/extraction with impact floor |
| `claude-opus-5-5` | 4 / .20 / 5; 8 / 20 | 1,000,000; max output 128,000 | Difficult judgment and cross-family review candidate |
| `claude-sonnet-5` | 2 / .2 / 2.5; 4 / 10 | 1,000,000 | Bounded work candidate |
| `claude-haiku-4-5-20251001` | 1 / .1 / 1.25; 2 / 5 | 200,000 | Mechanical work candidate |
| `claude-fable-5-1` | 10 / .25 / 12.5; 20 / 50 | 1,000,000 | Separately restricted premium pool |
| `grok-4.7` | 2 / .5 / n/a / 6 | 500,000 | Qualified build/review candidate |
| `grok-4.6` | 2 / .5 / n/a / 6 | 500,000 | Optional output-light measured candidate |

OpenAI GPT-6 API output ceiling is 128K. Its >272K prompt tier reprices the
**whole request**: input and cache at 2×, output at 1.5×. A local Codex catalog
observed a 272,000 base window and 872,000 extended limit; the live dispatch
surface governs, not the API maximum. OpenAI API reasoning effort is `none`,
`low`, `medium`, `high`, `xhigh`, `max`; a native schema may differ and also expose
`ultra` for Astra/Sol. The current local catalog describes `ultra` as automatic
task delegation, so it does not fit a no-delegation worker without live evidence
of bounded authorized behavior.

Opus 5.5 defaults to medium adaptive thinking, always on. Higher effort may use
more tokens than older Opus; there is no thinking-disabled/manual-budget shortcut,
and the API rejects forced `tool_choice: any` or `tool` for this model.
Verify CLI controls separately from API controls.
Grok 4.7 supports `low`, `medium`, `high`, `xhigh`, default high. At >=200K prompt
tokens, xAI doubles all token rates for the whole request. Check each call;
average tokens per turn cannot establish whether a particular request crossed
the threshold. `grok-build-0.1` is
an early-access 256K candidate at 1 / .2 / 2 input/read/output; a catalog listing
is not account access. Do not auto-select the harness-specific `grok-4.7-build-fast`.
`typesafe/jev-1.13` is a separate decision classifier at $0.042/M input,
$0 output and 32K context; see [Jev](https://openrouter.ai/typesafe/jev-1.13).
Legacy `gpt-5.6-terra` remains a possible qualified fallback;
`gpt-6-terra` was not in the verified current catalog.

For a purely illustrative 100K uncached input and 20K output call below the long
context tiers, standard API list prices are Astra $2.00, Sol $0.40, Luna $0.02,
Opus 5.5 $0.80, Grok 4.7 $0.32. These exclude tools, cache behavior, retries,
whole-route volume and service tier. Use the live runtime catalog and a successful exact-model request to establish
usable access. Only serving metadata establishes `SERVED` identity; a sign-in,
model list, or the model's self-report does not. Do not convert API dollars into subscription quota.

Primary sources: [OpenAI Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Sol](https://developers.openai.com/api/docs/models/gpt-6-sol),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna),
[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[Opus 5.5 behavior](https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5),
[Opus 5.5 limits](https://platform.claude.com/docs/en/models/opus-5-5/overview),
[xAI pricing](https://docs.x.ai/developers/pricing), and
[Grok 4.7](https://docs.x.ai/developers/models/grok-4.7).

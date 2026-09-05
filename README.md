# Astra Foreman

I built Astra Foreman to put my strongest Codex model on the decisions that matter:
understanding the job, choosing the crew, overseeing progress and accepting the
finished work. Bounded implementation can go to smaller capable agents, with
independent review for meaningful changes.

**v0.1.0 · Codex skill · MIT licensed**

[Get the ZIP and setup guide](https://www.dontsleeponai.com/astra-foreman).

## What I designed it to do

- Let Astra or Sol lead, with a complete Codex-only workflow.
- Use optional Claude or Grok routes when available and authorized.
- Apply preferences such as “favor Grok today” only to suitable roles, without
  giving a builder authority to approve its own work.
- Reassign work after quota limits or repeated attributable problems, preserving
  scope, ownership and independent verification.
- Keep a small written record of results, quality, availability and decisions.
- Interrupt unproductive review loops without treating a round limit as proof
  that unfinished work is good enough.

The instructions are in [SKILL.md](skills/astra-foreman/SKILL.md). Supporting
references load when needed. The Python standard-library helper records review
reservations; it does not launch agents, enforce spending, kill processes or
certify acceptance.

## Install and use

1. Download the versioned ZIP from the setup page.
2. Extract its `astra-foreman` folder.
3. Ask Codex to inspect that folder and install it in its user-level skills
   directory, preserving any existing installation before replacement.
4. In a new turn, invoke `$astra-foreman` with your task.

You're done when Codex recognizes the skill and explains its proposed scope,
verification and crew. Python 3.9+ is needed for the review helper. Available
agents, model controls and optional provider accounts depend on the runtime.
The skill does not supply subscriptions or bypass permissions.

Example:

```text
$astra-foreman Plan this build with me. Favor suitable Grok implementation work
today, keep independent review, and wait for my approval before implementing.
```

## What I have tested

The helper passes 12 dependency-free tests. Six bounded diagnostic scenarios
covered a live small coding task, provider preferences and quota changes, stalled
workers, noisy review findings, exhausted repair allowances and cold continuation
from a saved project. The outage/stall/repair events were simulated; the small
build and saved-project checks were live. Independent grading passed the batch.

These are initial checks, not evidence of guaranteed savings or multi-hour sprint
reliability. Native requested model identities were recorded separately from
unavailable independently confirmed serving/billing metadata. I recommend reading
the instructions and using a bounded, reversible task before a consequential run.

Run the helper tests from the repository root:

```sh
python3 -m unittest discover -s tests -v
```

## License and limits

MIT licensed; see [LICENSE](LICENSE). Use at your own risk. Independent model
review is a useful check, not a correctness guarantee. This release contains no
private development logs, account data or machine-specific configuration.

# Astra Foreman

![Astra Foreman](assets/astra-foreman-hero.png)

**v0.2.0 · Codex skill · MIT licensed · public release**

Astra Foreman keeps Astra or Sol in charge of understanding the outcome,
architecture, crew selection, supervision, independent review, and final
acceptance. For coherent substantive work, it delegates qualified builders
through authorized delivery: implementation, tests, routine repair, integration,
and permitted release operations.

## What it does

- Helps brainstorm and plan before implementation is authorized.
- Gives builders a clear contract and discretion over routine details and checks.
- Escalates material scope, architecture, interface, risk, and authority choices
  to the lead or user as appropriate.
- Preserves execution ownership across review and release gates; a gate pauses for
  evidence or judgment rather than making the lead the default builder.
- Uses independent review for meaningful changes and requires lead inspection of
  the actual candidate, evidence, critical user-facing or integration behavior,
  gaps, and disputes before acceptance.
- Routes by qualified capability, available provider capacity, user preferences,
  and the whole delivery cost without claiming guaranteed savings.
- Strongly prefers a qualified different-family challenge for substantial plans
  when an authorized route is already usable, with targeted cross-family review
  for consequential unresolved implementation questions.

Direct lead execution remains appropriate for answers, trivial inert edits, or a
tightly coupled fix when dispatch, supervision, review, repair, and integration
would cost more than doing it directly. Reassess at a safe checkpoint if that tail
becomes substantive.

## Install and use

The source and Git history are publicly available in the
[Astra Foreman repository](https://github.com/olsenbrands/astra-foreman).
That repository tracks `dist/astra-foreman-v0.2.0.zip`, and its public release
ZIP is downloadable without a site sign-in or checkbox acknowledgment.
The versioned ZIP is available from the public
[setup page](https://www.dontsleeponai.com/astra-foreman); that site download
requires a free signed-in DontSleepOnAI account and checkbox acknowledgment.

1. Inspect the public repository if you want to review the source and release
   history or download its ungated public release ZIP.
2. To obtain the packaged ZIP from the setup page, sign in to a free
   DontSleepOnAI account, acknowledge the checkbox, then download and unpack
   `astra-foreman-codex-v0.2.0.zip`.
3. Ask Codex to inspect and install the included `astra-foreman` folder in its
   user-level skills directory, preserving an existing installation before
   replacement.
4. Start a new Codex session and invoke `$astra-foreman` with the task.

Python 3.9+ is required only for the dependency-free review-reservation helper.
Available agents, model controls, and optional provider accounts depend on the
runtime. The skill neither supplies subscriptions nor bypasses permissions.

Example:

```text
$astra-foreman Plan this build, delegate the substantive delivery to qualified
workers, retain independent review, and wait for my approval before deployment.
```

## Validation and limits

The included helper has a dependency-free test suite. This release also receives
focused package checks and a scenario review of its delivery, repair, review, and
acceptance boundaries. Those checks support this package; they do not prove
multi-hour reliability or guaranteed cost savings.

See [SKILL.md](skills/astra-foreman/SKILL.md), supporting references, and the
[changelog](CHANGELOG.md). The skill package contains no account data,
machine-specific configuration, private logs, or private project history.

## License

MIT licensed; see [LICENSE](LICENSE). Independent review is a useful check, not a
correctness guarantee.

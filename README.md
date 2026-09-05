# Astra Foreman

![Astra Foreman](assets/astra-foreman-hero.png)

**v0.1.1 · Codex skill · MIT licensed**

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

Direct lead execution remains appropriate for answers, trivial inert edits, or a
tightly coupled fix when dispatch, supervision, review, repair, and integration
would cost more than doing it directly. Reassess at a safe checkpoint if that tail
becomes substantive.

## Install and use

1. Download the versioned ZIP from the setup page.
2. Extract the `astra-foreman` folder.
3. Ask Codex to inspect and install it in its user-level skills directory,
   preserving an existing installation before replacement.
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
[changelog](CHANGELOG.md). This public package contains no account data,
machine-specific configuration, private logs, or private project history.

## License

MIT licensed; see [LICENSE](LICENSE). Independent review is a useful check, not a
correctness guarantee.

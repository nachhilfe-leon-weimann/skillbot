# SkillBot docs

What the bot must do and why. SkillForge stopped being the bot's backend ([ADR 0009][adr-0009]); the Discord rules
it used to enforce are written down here, and the bot rebuilds them on its own database ([#22][rebuild]).

## Specs

| Page                                                  | Holds                                                                  |
| ----------------------------------------------------- | ---------------------------------------------------------------------- |
| [Workspaces](specs/workspaces.md)                     | tutor and student workspaces, capacity, archive categories, teardown order |
| [Reservations](specs/reservations.md)                 | how a Discord change is reserved, replayed, expired and cancelled      |
| [Off-boarding](specs/off-boarding.md)                 | what ends a workspace and what it never touches                        |
| [Command environments](specs/command-environments.md) | which channel a kind of command runs in                                |
| [Topology and roles](specs/topology-and-roles.md)     | guild, channels, members, roles - and what changes                     |
| [SkillForge contracts](specs/skillforge-contracts.md) | pulling, the token exchange, errors, `/link`                           |

[Decisions](decisions/README.md) holds the inherited decisions and the questions still open.

## References

- A rule read out of the code SkillForge removes links SkillForge's tag [`v0.5.0`][v050], which keeps that code, its
  tests and its bot specs. A contract SkillForge keeps links SkillForge's `main`.
- Code is named by symbol, never by line number.

## Reference material at SkillForge `v0.5.0`

- **Tests:** [`test_bot_transitions_service.py`][t-transitions] (55 items, the concurrency tests included),
  [`test_bot_operations_service.py`][t-operations], [`test_bot_reaper_service.py`][t-reaper],
  [`test_bot_jobs_service.py`][t-jobs].
- **Specs:** [lifecycle guardian][s-guardian], [off-boarding transitions][s-offboarding],
  [operation cancel][s-cancel], [ops read plane][s-ops], [principals and provisioning][s-principals],
  [batch lookups][s-batch].
- **Decisions:** [ADR 0003][adr-0003] and [ADR 0004][adr-0004], superseded by ADR 0009.
- **Closed issues with unticked criteria:** SkillForge [#4][i4], [#47][i47], [#48][i48], [#50][i50] and [#52][i52].
  The bot has built none of their rules yet; what SkillForge built is in the specs above, and #47's retention
  question is [open](decisions/README.md#to-decide).

[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[rebuild]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/22
[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[t-transitions]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/tests/db/test_bot_transitions_service.py
[t-operations]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/tests/db/test_bot_operations_service.py
[t-reaper]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/tests/db/test_bot_reaper_service.py
[t-jobs]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/tests/db/test_bot_jobs_service.py
[s-guardian]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/lifecycle-guardian.md
[s-offboarding]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/off-boarding-transitions.md
[s-cancel]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/operation-cancel.md
[s-ops]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/ops-read-plane.md
[s-principals]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/principals-and-provisioning.md
[s-batch]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/batch-lookups.md
[adr-0003]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0003-two-phase-transitions.md
[adr-0004]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0004-forge-first-job-queue.md
[i4]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/4
[i47]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/47
[i48]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/48
[i50]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/50
[i52]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/52

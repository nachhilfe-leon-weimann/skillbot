# Decisions

SkillBot's architecture decisions, one file each (`NNNN-title.md`). It has none of its own yet.

## Inherited from SkillForge

- [ADR 0009][adr-0009] - the bot owns its Discord workflows; SkillForge keeps central data and pushes nothing.
  Accepted, 2026-09.
- [ADR 0003][adr-0003] - two-phase `prepare`/`commit` for Discord state. Superseded by 0009; its rules live on in
  [Reservations](../specs/reservations.md).
- [ADR 0004][adr-0004] - the job queue with at-least-once delivery. Superseded by 0009; its lease and sweeper are in
  [Reservations](../specs/reservations.md#lease-and-sweeper).

## To decide

Open for the business. The specs record what SkillForge `v0.5.0` did; neither answer is taken here.

- **One tutor per student, or several?** The CRM allows several: a `TUTOR_OF` relation is keyed by both parties and
  its type ([`PartyRelation`][m-relation]). At `v0.5.0` a student had one workspace per guild under exactly one
  tutor ([`StudentWorkspace`][m-student]), and a second tutor's activation was refused
  ([Workspaces](../specs/workspaces.md#transitions)).
- **Archive or delete a workspace on off-boarding, and how long to keep it?** At `v0.5.0` off-boarding deleted the
  student channel and the workspace rows; only the committed operation row stayed, with no retention. The archive
  categories held stashed students, not off-boarded ones ([Off-boarding](../specs/off-boarding.md)). SkillForge
  [#47][i47] left this criterion unticked.

## Settled

- An explicit deny for one person has no successor: disable the account or remove the role ([ADR 0009][adr-0009],
  "No second rights system").

[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[adr-0003]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0003-two-phase-transitions.md
[adr-0004]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0004-forge-first-job-queue.md
[m-relation]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/core/party_relation.py
[m-student]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/student_workspace.py
[i47]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/47

# Spec: Off-boarding

> Status: Handover from SkillForge [`v0.5.0`][v050] ([#21][issue]), with the triggers of SkillForge's
> [bot-decoupling arc][handover].

## What triggers it

The CRM holds the intended state ([ADR 0009][adr-0009], point 4); the bot pulls it and tears a workspace down when
([pull contract][change-signals], rule 11):

- the person's tutor or student role is removed,
- the `TUTOR_OF` between tutor and student is removed, or
- the person's Discord link is deactivated - the link feed returns unlinked rows.

Disabling an account off-boards nobody. Removing a role also removes the `TUTOR_OF` it anchored
([decision O][decisions]), so the other side of each pair moves in the feed as well. For a tutor, the students go
first ([teardown order](workspaces.md#teardown-order)).

## What it never touches

- **No CRM data.** Off-boarding never writes the CRM and never blocks a CRM write (ADR 0009, point 4). At `v0.5.0`
  the only identity it changed was the bot's own: `DiscordUser.active` = false (`_deactivate_user`: "Party/CRM data
  is never touched").
- A person with an active Discord link cannot be deleted in the CRM; the unlink comes first and reaches the bot
  through the link feed ([pull contract][change-signals], rule 10).

## The teardown at `v0.5.0`

- **`student_deactivate`** works from either state - a stashed student is off-boarded without a pop. The plan is
  `delete_student_channel` with the channel; the commit deletes the student workspace and its channel row and flips
  the student's `active` off (`commit_student_deactivation`, [`transitions.py`][transitions]).
- **`tutor_deactivate`** follows the [teardown order](workspaces.md#teardown-order): only a tutor without students
  and inbound reservations; the plan is `delete_tutor_workspace` with the category and the command channel.
- A prepared `student_deactivate` frees no capacity; its commit does ([tutor capacity](workspaces.md#tutor-capacity)).
- Workspace and channel rows are **deleted**; the committed operation row is the record that stays. Re-onboarding is
  a fresh activation.
- There is no cascade: a tutor teardown never tears down the tutor's students (P1-1 of
  [off-boarding transitions][s-offboarding], never built).

## Open

- **Archive or delete, and how long to keep it,** is the bot's decision and still open
  ([decisions](../decisions/README.md#to-decide)). At `v0.5.0` off-boarding deleted the channel; the archive
  categories held stashed students only.

[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[handover]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#handover-to-skillbot
[decisions]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#decisions
[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[change-signals]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/ARCHITECTURE.md#change-signals
[transitions]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/transitions.py
[s-offboarding]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/off-boarding-transitions.md

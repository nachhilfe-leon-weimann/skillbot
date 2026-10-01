# Spec: Workspaces

> Status: Handover from SkillForge [`v0.5.0`][v050] ([#21][issue]) - what SkillForge enforced for the bot until
> [ADR 0009][adr-0009]. The bot keeps these rules on its own database.

## Shape

- **Tutor workspace** ([`TutorWorkspace`][m-tutor]): one Discord category and one command channel inside it, per
  tutor and guild.
- **Student workspace** ([`StudentWorkspace`][m-student]): one text channel per student and guild, under exactly one
  tutor. Its `channel_state` is one of:
  - `tutor_category` - the channel sits in its tutor's category;
  - `archive_category` - the channel is _stashed_ in an archive category. A stash parks a student; it does not
    off-board them.
- **Archive category** ([`ArchiveCategory`][m-archive]): an overflow category of the guild for stashed students,
  numbered by `archive_no`.
- The checks on `StudentWorkspace` keep the state coherent: `archive_category` needs a channel and an archive
  category, and that category is the channel's parent; `tutor_category` has no archive category.

## Transitions

Each one is a reservation first ([Reservations](reservations.md)), then a commit ([`transitions.py`][transitions]).

| Transition           | Needs                                                                              | The commit                                                   |
| -------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `tutor_activate`     | the guild, an active tutor, no tutor workspace yet                                 | records both channels, creates the workspace                 |
| `student_activate`   | the guild, an active student, `TUTOR_OF`, the tutor's workspace, a free tutor slot | records the channel under the tutor's category               |
| `student_stash`      | the workspace in `tutor_category`, a free archive slot                             | moves it to the reserved archive category, sets `stashed_at` |
| `student_pop`        | the workspace in `archive_category`, the tutor's workspace, a free tutor slot      | moves it back under the tutor's category, sets `popped_at`   |
| `student_deactivate` | the workspace, in either state                                                     | see [Off-boarding](off-boarding.md)                          |
| `tutor_deactivate`   | the tutor's workspace, no students, no inbound reservations                        | see [Teardown order](#teardown-order)                        |

- **`TUTOR_OF`** ([`_require_tutor_of`][transitions]): both Discord users must be linked to a party through an
  **active** link - any active link of the party will do - and the tutor's party must have `TUTOR_OF` to the
  student's. The commit does not ask again: a relation gone between the phases is divergence to reconcile, not a
  failed commit.
- A student has one workspace per guild: an activation under another tutor is refused while the first is reserved
  ([Reservations](reservations.md#the-natural-key)), and every activation once it is committed - 409 "Student
  workspace already exists". Whether a student may have several tutors is [open](../decisions/README.md#to-decide);
  this is what `v0.5.0` enforced.

## Tutor capacity

- **Bounds:** `student_channel_capacity` is **0..49**, default 49 (`ck_tutor_workspace_student_channel_capacity`).
  At 0 the tutor takes no student.
- **Counted** ([`_assert_tutor_capacity`][transitions]): the tutor's student workspaces in `tutor_category`, plus
  its live inbound reservations - `PREPARED` `student_activate` and `student_pop` operations whose `expires_at` lies
  in the future (`_TUTOR_CATEGORY_INBOUND_KINDS`).
- **Not counted:** stashed students (`archive_category`); expired and cancelled reservations; a prepared
  `student_deactivate` - it frees nothing, the slot comes back when its commit deletes the workspace
  (`test_student_deactivation_frees_tutor_capacity`).
- **Full** when counted >= capacity: `TransitionConflictError` (409) "Tutor student capacity reached"
  (`test_student_activation_capacity_counts_reservations`).
- **Where:** in `prepare_student_activation` and `prepare_student_pop`, under the tutor workspace's row lock
  (`_lock_tutor_workspace`, `FOR UPDATE`) and after the retry lookup. No commit counts again; the reservation holds
  the slot until it expires.

## Archive categories

- **Bounds:** `capacity` is **1..50**, default 50 (`ck_archive_category_capacity`); `archive_no` > 0
  (`ck_archive_category_archive_no_positive`).
- **First fit by `archive_no`** ([`_reserve_archive_slot`][transitions]): lock every archive category of the guild
  `FOR UPDATE` in `archive_no` order and take the first whose stashed students plus live `PREPARED` `student_stash`
  reservations for it stay below its capacity. The reservation records the category
  (`reserved_archive_category_channel_id`) and the plan names it (`archive_no`, `archive_category_channel_id`); a
  retry keeps it (`test_repeated_stash_prepare_returns_same_operation`).
- **None configured:** `TransitionValidationError` (422) "No archive category configured for this guild"
  (`test_stash_requires_archive_category`).
- **All full:** `TransitionConflictError` (409) "All archive categories are full"
  (`test_stash_capacity_full_across_archives`).

## Teardown order

- **Students before their tutor.** A tutor teardown is refused while any student workspace names the tutor - in
  **either** state - or any live inbound reservation (`student_activate`, `student_pop`) exists for it
  ([`_assert_tutor_has_no_students`][transitions]): 409 "Tutor still has student workspaces" or "Tutor has
  outstanding inbound reservations". There is no cascade.
- **Checked twice, under the lock.** `prepare_tutor_deactivation` checks under the tutor workspace's row lock;
  `commit_tutor_deactivation` takes the lock again and checks again. A prepared teardown does not stop a student
  activation in between - the commit's check is what refuses (`test_tutor_deactivation_commit_rechecks_no_students`,
  `test_tutor_deactivation_commit_rechecks_reservations`,
  `test_tutor_deactivation_commit_serializes_against_concurrent_reservation`).
- **A child channel goes before its category** - in Discord and in the records: `commit_tutor_deactivation` deletes
  the command channel (child) before the category (parent), then flips the tutor's `active` off.

[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[transitions]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/transitions.py
[m-tutor]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/tutor_workspace.py
[m-student]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/student_workspace.py
[m-archive]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/archive_category.py

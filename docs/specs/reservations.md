# Spec: Reservations

> Status: Handover from SkillForge [`v0.5.0`][v050] ([#21][issue]). SkillForge planned every Discord change in two
> phases ([ADR 0003][adr-0003]): `prepare` checked and reserved, the bot changed Discord, `commit` recorded the
> result. [ADR 0009][adr-0009] moves this into the bot as "an internal saga with its own locks"; these are the
> semantics it keeps.

## The reservation

- A prepare writes an [`Operation`][m-operation] in status `PREPARED` with a `plan` and
  `expires_at` = now + `OPERATION_TTL` (**10 minutes**, [`transitions.py`][transitions]).
- Kinds: `tutor_activate`, `student_activate`, `student_stash`, `student_pop`, `student_deactivate`,
  `tutor_deactivate`. Statuses: `prepared`, `committed`, `expired`, `cancelled`, `failed` - nothing sets `failed`.
- Only a **live** reservation - `PREPARED` with `expires_at` in the future - counts for capacity and for the retry
  lookup.
- A commit needs a live `PREPARED` reservation of its own kind (`_load_prepared_operation`): unknown or another
  kind is 404; not `PREPARED` is 409 "Operation is not in a prepared state"; one past its TTL is 409 "Operation
  has expired".
- Terminal rows are kept; nothing purges them.

## The natural key

- A reservation's identity is **(guild, subject, kind)** - `guild_id`, `subject_discord_id`, `kind`.
- **A retry replays.** Every prepare looks up the live reservation of its key (`_find_open_operation`) and returns
  it unchanged: same id, same plan, same archive category.
- **The `_require_*` checks run before the lookup,** so every retry is validated again: a retried student activation
  whose `TUTOR_OF` is gone is refused, not replayed
  (`test_a_retried_student_activation_is_validated_again_not_replayed`).
- **Counts run after the lookup,** so a retry at full capacity replays instead of tripping over its own
  reservation (`test_retried_activation_near_capacity_replays_without_capacity_error`,
  `test_retried_stash_when_archive_full_replays_without_conflict`,
  `test_retried_pop_near_capacity_replays_without_capacity_error`).
- **A different tutor conflicts.** Only `student_activate` names its tutor. A live reservation of the student under
  another tutor is 409 "Subject already has an operation prepared under a different tutor"
  (`_replayed_or_conflict`), never a replay (`test_student_activation_prepare_conflicts_on_different_tutor`).

## Expired and cancelled

- **Expired** is a timeout. A reservation stops counting the instant its TTL passes; its status becomes `expired`
  when the sweeper runs or when a prepare of its key collides with it.
- **The lazy flip does not stick.** A commit or cancel that finds an expired reservation marks it `expired` and then
  raises; the error rolls the request's transaction back ([`Database.session`][database]), so the row stays
  `PREPARED` until the sweeper or a colliding prepare.
- **An expired but unswept reservation is reclaimed.** A prepare never replays it
  (`test_prepare_after_expiry_creates_new_operation`); when it still holds the unique slot, the prepare flips it to
  `expired` and inserts a new one (`_expire_stale_prepared`, `test_prepare_reclaims_expired_row_holding_the_slot`).
- **Cancelled** is an explicit abort (`cancel_operation`, [operation cancel][s-cancel]): a live `PREPARED`
  reservation becomes `cancelled` with `cancelled_at` and frees its slot and its key at once. Cancelling a
  `cancelled` one returns it unchanged; `committed`, `expired` or `failed` is 409; unknown is 404.
- **Cancelled differs from expired:** a reservation past its TTL is `expired`, never `cancelled` - even when the
  cancel arrives just after the TTL (409 "Operation has expired").
- **Known gap:** a commit and a cancel of the same reservation are not locked against each other. The terminal
  label can diverge from what happened; capacity stays right ([operation cancel][s-cancel], its decisions).

## The race

Two prepares of one key in parallel transactions do not see each other's uncommitted insert, so a lookup alone would
book twice. Commit [`072c3b7`][c-072c3b7] (SkillForge [#48][i48]) closes it:

- **A partial unique index**, `uq_operation_prepared_subject_kind` on (`guild_id`, `subject_discord_id`, `kind`)
  where the status is `prepared`. It cannot filter on `expires_at` (`now()` is not immutable), so an expired row
  keeps its slot in the index until it is reclaimed or swept.
- **A savepoint insert** (`_create_operation`): add and flush inside `begin_nested()`, so a unique violation rolls
  back only the insert. Then a live winner is replayed - or is the different-tutor 409; otherwise the collider is
  expired: reclaim it and insert again. After `_CREATE_MAX_ATTEMPTS` (3) the live winner is replayed, or 409 "Could
  not reserve an operation slot".
- **The lock before the lookup.** Activation and pop lock the tutor workspace before the lookup. Stash locks the
  student workspace `FOR UPDATE` before it, because its other lock - the archive categories - comes only inside
  `_reserve_archive_slot`; without it a parallel retry counted the winner's reservation and answered "archive
  full". Two activations of one student under different tutors lock different rows; only the index catches them.
- Tests: `test_concurrent_prepare_dedupes_to_a_single_operation`,
  `test_concurrent_activation_under_different_tutor_conflicts`,
  `test_concurrent_stash_same_student_replays_without_capacity_error`.

## Lease and sweeper

From the [lifecycle guardian][s-guardian] ([`reaper.py`][reaper], [`app/workers/reaper.py`][worker]):

- **Sweeper:** every `REAPER_INTERVAL` (30 s) one bulk update flips `PREPARED` rows past `expires_at` to `expired`
  (`sweep_expired_operations`). Idempotent, never touches a terminal row, frees nothing new - an expired reservation
  stopped counting at its TTL.
- **Lease:** a job claimed more than `JOB_LEASE` (5 min) ago is reclaimed through the retry path of `fail_job`: back
  to `PENDING` after `RETRY_BACKOFF` (60 s), or `FAILED` - the dead letter - once `attempt` reached `max_attempts`
  (default 5). The reclaim costs no extra attempt; `FOR UPDATE SKIP LOCKED` keeps two guardians apart; batches of
  `REAP_BATCH_LIMIT` (100).
- **At least once:** a reclaimed job is delivered again, so every handler must be idempotent ([ADR 0004][adr-0004]).

[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[adr-0003]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0003-two-phase-transitions.md
[adr-0004]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0004-forge-first-job-queue.md
[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[m-operation]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/operation.py
[transitions]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/transitions.py
[reaper]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/reaper.py
[worker]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/workers/reaper.py
[database]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/database.py
[s-cancel]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/operation-cancel.md
[s-guardian]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/specs/lifecycle-guardian.md
[c-072c3b7]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/commit/072c3b780ba4fdf934d24f962d6727cd66491cd2
[i48]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/issues/48

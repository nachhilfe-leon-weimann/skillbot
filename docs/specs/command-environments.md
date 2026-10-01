# Spec: Command environments

> Status: Handover from SkillForge [`v0.5.0`][v050] ([#21][issue]).

A command environment allows one kind of command in one channel ([`CommandEnvChannel`][m-cmdenv],
[`command_envs.py`][svc-cmdenv]).

- **Kinds:** `admin_cmd` and `tutor_cmd`. The bot's own `CommandEnvKind.teacher_cmd` ([`models.py`][sb-models])
  becomes `tutor_cmd`.
- **Key:** (guild, channel, kind) - one channel can carry both kinds.
- **At most one per kind per owner per guild** (`uq_command_env_channel_guild_id_owner_discord_id_kind`, only where
  an owner is set). Environments without an owner are not limited.
- **Keyed by `party_id`:** `v0.5.0` stored the owner as `owner_discord_id`; the rebuild keys the owner by the
  person's `party_id`.
- **Writing** (`upsert_command_env`): the channel must be known in that guild and the owner must exist (422); an
  owner who already owns another channel of that kind in the guild is 409 - checked first, with the unique index as
  the backstop inside a savepoint. Writing an existing (guild, channel, kind) replaces its owner.
- **Resolving** (`resolve_command_env`): guild, channel and kind must match, and the owner too when one is asked
  for; otherwise 404.
- **Lifetime:** an environment goes with its channel and with its owner (`ON DELETE CASCADE` on both).
- **Not tied to a workspace:** no transition writes a command environment; a tutor workspace's
  `command_channel_id` and a `tutor_cmd` environment are separate records.

[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[m-cmdenv]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/command_env_channel.py
[svc-cmdenv]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/command_envs.py
[sb-models]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/blob/v0.1.0/src/skillbot/core/models.py

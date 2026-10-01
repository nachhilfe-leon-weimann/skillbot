# Spec: Topology and roles

> Status: Handover from SkillForge [`v0.5.0`][v050] ([#21][issue]), with what SkillForge's
> [bot-decoupling arc][handover] changes.

## Topology at `v0.5.0`

- **Guild** ([`DiscordGuild`][m-guild]): `guild_id`, `name`, `is_primary`, `active`; at most one primary active
  guild (`uq_discord_guild_primary_active`). The two activations require the guild (`_require_guild`, 422 "Guild
  not found").
- **Channel** ([`DiscordChannel`][m-channel]): `channel_id`, `guild_id`, `parent_channel_id` (a parent in the same
  guild), `type` (`category`, `text`, `voice`, `thread`, `forum`), `managed_by_bot`, `deleted_at`. A commit records
  the channels the bot created (`_ensure_channel`) and deletes the rows of the channels it deleted
  (`_delete_channel`); both are idempotent. Nothing sets `deleted_at`.
- **Member** ([`DiscordUser`][m-user]): `discord_id`, `role` (`admin`, `tutor`, `student`), `nick_name` (not
  empty), `active`. The bot wrote it with an idempotent upsert (`upsert_discord_user`); a transition requires an
  active member of the right role (`_require_active_user`); off-boarding flips `active` off.
- **Role binding** ([`DiscordRoleBinding`][m-binding]): per guild and member role, a Discord `role_id` (optional)
  and a `role_name` (required).

## What changes

- **Keys:** the bot's records are keyed by `party_id` - a plain key taken from SkillForge's API
  ([ADR 0009][adr-0009], point 3) - and by Discord role IDs, never by role names.
- **Roles project from SkillForge to Discord only, never back.** No Discord role grants a right - a role name least
  of all (ADR 0009, "No second rights system").
- **The role-name fallback goes:** `_fallback_role_from_discord` ([`service.py`][sb-permissions]) turned a member's
  Discord role _name_ into a member role - admin included - through `DiscordRoleResolver`
  ([`discord_roles.py`][sb-roles]).
- **The grant engine goes** with no successor: permission groups and user, group and role grants, where the grant
  of the highest priority wins and a tie denies ([`principals.py`][principals]). SkillForge's scopes and reach
  decide, for the person's token.
- **The delegation check goes:** `check_authorization` ([`authz.py`][authz]) let an actor act on its own party and
  on the targets of its `PARENT_OF` and `PAYS_FOR` relations, never through `TUTOR_OF`. SkillForge's reach answers
  that now.
- The bot's `MemberRole.teacher` ([`models.py`][sb-models]) becomes `tutor`, as in SkillForge.

[v050]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/tree/v0.5.0
[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[handover]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#handover-to-skillbot
[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md
[m-guild]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/discord_guild.py
[m-channel]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/discord_channel.py
[m-user]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/discord_user.py
[m-binding]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/core/db/models/bot/discord_role_binding.py
[principals]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/principals.py
[authz]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/app/services/bot/authz.py
[sb-permissions]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/blob/v0.1.0/src/skillbot/core/permissions/service.py
[sb-roles]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/blob/v0.1.0/src/skillbot/core/discord_roles.py
[sb-models]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/blob/v0.1.0/src/skillbot/core/models.py

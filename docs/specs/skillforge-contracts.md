# Spec: SkillForge contracts

> Status: What SkillForge keeps after its [bot-decoupling arc][bot-decoupling] ([#21][issue]). The contracts live
> in SkillForge's `main`; this page names the bot's side of each.

- **Pulling.** The [pull contract][change-signals] (SkillForge's "Change signals") is the one source. The bot runs
  its consumer defaults: poll every 60 s, overlap 5 minutes, full comparison every 30 minutes, skip an item whose
  (`id`, `updated_at`) equals the stored one. The sync only reads.
- **Acting as the person.** The [token exchange][exchange] gives the bot a token for the Discord user who sent a
  command. [The bot's side][bot-side]:
  - cache tokens per (`discord_user_id`, requested scope) until shortly before `expires_in`, single-flight per key,
    in memory only; re-exchange once on a 401; cap concurrent exchanges - each costs one Argon2 check of the client
    secret;
  - exchange only for `interaction.user.id`, never for an ID from command options, and only for users with an
    active link in the local copy; evict on a deactivated link;
  - `invalid_grant` means "offer only what needs no identity", `invalid_scope` means "not permitted";
  - the application token is for the sync only.
- **Errors.** Branch on the error envelope's `code` ([ADR 0006][adr-0006]), never on `detail`.
- **`/link <code>`** ([one-time link code][link-code]): reply ephemerally, apply a per-user cooldown, always send
  `interaction.user.id` - as a decimal string, like every Discord user ID on SkillForge's wire (its decision I).
- **No tutor command acts on a student through SkillForge** until SkillForge's reach arc makes "only the student's
  own tutor" a rule; the bot does not rebuild it from roles and 404 probes ([ADR 0009][adr-0009]).
- **The bot never writes a Discord link as itself,** and its client never holds `auth:users:manage`,
  `auth:clients:manage` or `auth:users:login` ([security rules][security]).

[issue]: https://github.com/Nachhilfe-Leon-Weimann/skillbot/issues/21
[bot-decoupling]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md
[change-signals]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/ARCHITECTURE.md#change-signals
[exchange]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#token-exchange
[bot-side]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#the-bots-side-of-the-contract
[link-code]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#one-time-link-code-p1-1
[security]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/specs/bot-decoupling.md#security-rules
[adr-0006]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/v0.5.0/docs/decisions/0006-error-envelope.md
[adr-0009]: https://github.com/Nachhilfe-Leon-Weimann/skillforge/blob/main/docs/decisions/0009-bot-owns-its-discord-workflows.md

# ADR-006: Typed Configuration System

- Status: Accepted
- Date: 2026-07-23

## Problem

InstaOS needs predictable configuration across local scanning, scheduled jobs,
AI pipelines, publishing accounts, storage backends, and future cloud hosts.
Ad-hoc `os.environ` access spreads secrets and validation logic through the
codebase, makes tests non-deterministic, and does not scale to nested settings.

## Alternatives

1. **Plain dictionaries and `os.environ`**: minimal dependency cost, but no
   schema, validation, secret type, or reliable nested merge semantics.
2. **Dataclasses plus a custom parser**: strong Python typing, but duplicates
   environment, dotenv, URL, and validation work.
3. **Pydantic Settings with a manager and explicit source loader**: typed,
   immutable models; environment-aware configuration; safe error handling; and
   a clear extension point for future sources.

## Decision

Use Pydantic Settings for the `ApplicationSettings` schema and a per-instance
`ConfigManager` for source loading, precedence, caching, validation, and safe
serialization. Support JSON, YAML, `.env`, environment variables, and runtime
overrides. Secrets are represented by `SecretStr` and are always redacted in
exports. Configuration source priority is runtime, environment, dotenv, file,
then defaults.

## Tradeoffs

Pydantic and YAML parsing add dependencies and startup validation work. This is
accepted because parsing happens once per manager and the immutable result is
cached. Explicit source merging is more code than relying only on BaseSettings,
but makes precedence consistent across YAML/JSON and test-injected environments.

## Future Work

Add authenticated cloud configuration source adapters, Kubernetes secret-file
support, configuration revision telemetry without values, and controlled live
reload coordination for long-running worker processes. Keep these additions at
the loader boundary and preserve the `ApplicationSettings` contract.

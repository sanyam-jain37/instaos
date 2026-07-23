# ADR-007: Publisher Abstraction

## Decision

Use a provider-neutral `Publisher` contract with immutable requests/results and
typed failures. Provider construction is centralized in `PublisherFactory`.

## Tradeoffs

The abstraction adds a small indirection, but keeps retries, scheduler code,
and future Graph API logic independent of platform-specific implementation.

## Future work

Implement the Instagram Graph API client behind `InstagramPublisher`; preserve
the current request/result contract and never pass raw credentials to logs.

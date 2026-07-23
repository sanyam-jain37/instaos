# Publishers

`Publisher` isolates social-platform behavior behind `validate`, `publish`,
`health_check`, and `delete_post`. `MockPublisher` is deterministic and used by
tests. `InstagramPublisher` validates requests and reports configuration state,
but deliberately makes no network calls until Graph API integration is added.

Use `RetryPolicy` around publisher calls. It retries only typed retryable errors,
caps attempts, and accepts an injectable sleeper for deterministic tests.

To add a provider, implement `Publisher`, add it to `PublisherFactory`, and keep
credentials in configuration/secret storage rather than provider source code.

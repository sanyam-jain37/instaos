# InstaOS Configuration System

## Architecture

`ConfigManager` is the process-local configuration boundary. It loads JSON,
YAML, dotenv, environment, and runtime values into one immutable
`ApplicationSettings` instance. Services receive the validated settings object
through dependency injection; they do not parse environment variables.

```text
YAML/JSON -> .env -> process environment -> runtime overrides
                                                |
                                                v
                                     ConfigManager + Pydantic Settings
                                                |
                                                v
                                  immutable ApplicationSettings (cached)
```

The precedence order is runtime overrides, process environment, `.env`, config
file, then typed defaults. `load()` caches the validated object. `reload()` is
the only operation that re-reads sources.

## Usage

```python
from pathlib import Path

from app.config import ConfigManager

manager = ConfigManager(config_path=Path("config/production.yaml"))
settings = manager.load()
database_url = settings.database.url
```

Use explicit runtime overrides for tests and hosting environments:

```python
manager = ConfigManager(
    env_file=None,
    overrides={"application": {"environment": "test"}},
)
settings = manager.load()
```

## Environment variables

All environment variables begin with `INSTAOS_`; nested values use `__`.

```dotenv
INSTAOS_APPLICATION__ENVIRONMENT=production
INSTAOS_APPLICATION__API_PORT=8080
INSTAOS_DATABASE__URL=postgresql://user:password@db/instaos
INSTAOS_LOGGING__LEVEL=INFO
INSTAOS_STORAGE__BACKEND=s3
INSTAOS_STORAGE__BUCKET=instaos-assets
INSTAOS_AI_PROVIDERS__PROVIDERS=[
  {"name":"primary","model":"gpt","enabled":true,"api_key":"set-in-secret-store"}
]
```

Complex lists and mappings in environment variables must be JSON encoded.
Environment values override `.env` and persisted files.

## YAML example

```yaml
application:
  environment: production
  api_port: 8080
database:
  url: sqlite:///data/instaos.db
google_drive:
  enabled: true
  root_folder_id: root
scheduler:
  enabled: true
  timezone: Asia/Kolkata
logging:
  level: INFO
storage:
  backend: local
  local_directory: data/assets
instagram:
  enabled: false
```

## JSON example

```json
{
  "application": {"environment": "development", "api_port": 8000},
  "database": {"url": "sqlite:///data/instaos.db"},
  "scheduler": {"enabled": false},
  "storage": {"backend": "local", "local_directory": "data/assets"}
}
```

## Validation

The schema validates ports, database URL schemes, HTTP URLs, path safety,
required enabled-provider credentials, unique Instagram account IDs/usernames,
unique provider and publisher names, S3 bucket requirements, and blank or short
secrets. Validation errors omit submitted secret values.

## Security

Never put access tokens or API keys in tracked YAML/JSON files. Keep them in a
secret manager, deployment environment, or ignored `.env` file. `export_json`,
`export_yaml`, and `save` always redact `SecretStr` values as `********`; they
cannot produce a recoverable secrets backup. Do not log settings objects or
exception input payloads.

## Future cloud configuration

Cloud providers should materialize an already-authorized mapping and pass it as
runtime overrides, preserving the same schema and precedence rules. A future
cloud source adapter belongs beside `ConfigurationLoader`; no service should
bypass `ConfigManager`.

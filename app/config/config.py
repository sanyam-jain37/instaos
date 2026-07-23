"""High-level configuration manager for InstaOS."""

from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import (
    AnyUrl,
    BaseModel,
    SecretStr,
    ValidationError as PydanticValidationError,
)

from app.config.exceptions import ConfigurationError, ValidationError
from app.config.loader import ConfigurationFormat, ConfigurationLoader, deep_merge
from app.config.models import ApplicationSettings
from app.config.validators import REDACTED_SECRET_VALUE


class ConfigManager:
    """Loads, validates, caches, and safely exports application configuration.

    Configuration precedence is runtime overrides, process environment, dotenv,
    persisted file, and finally schema defaults.
    """

    def __init__(
        self,
        config_path: Path | None = None,
        env_file: Path | None = Path(".env"),
        overrides: Mapping[str, Any] | None = None,
        environment: Mapping[str, str] | None = None,
        loader: ConfigurationLoader | None = None,
    ) -> None:
        """Initializes a configuration manager and its source locations.

        Args:
            config_path: Optional YAML or JSON base configuration file.
            env_file: Optional dotenv file. Set to ``None`` to disable it.
            overrides: Runtime values with the highest precedence.
            environment: Optional process environment override for tests or hosts.
            loader: Optional source loader implementation.
        """
        self._config_path = config_path
        self._env_file = env_file
        self._overrides = dict(overrides or {})
        self._environment = dict(environment) if environment is not None else None
        self._loader = loader or ConfigurationLoader()
        self._cached_settings: ApplicationSettings | None = None

    def load(self) -> ApplicationSettings:
        """Loads and caches validated application configuration.

        Returns:
            Immutable validated application settings.

        Raises:
            ConfigurationError: If a source cannot be loaded or validated.
        """
        if self._cached_settings is None:
            self._cached_settings = self._build_settings()
        return self._cached_settings

    def reload(self) -> ApplicationSettings:
        """Invalidates the cache and reloads all configuration sources.

        Returns:
            Newly validated immutable application settings.
        """
        self._cached_settings = None
        return self.load()

    def save(
        self,
        path: Path,
        configuration_format: ConfigurationFormat | None = None,
    ) -> Path:
        """Writes a redacted configuration export to a JSON or YAML file.

        Args:
            path: Destination file path.
            configuration_format: Explicit target format, inferred from path when
                omitted.

        Returns:
            The written destination path.
        """
        target_format = configuration_format or self._loader.format_for_path(path)
        content = self._loader.dump(self._safe_mapping(), target_format)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def validate(self) -> ApplicationSettings:
        """Loads and returns validated configuration.

        Returns:
            Immutable validated application settings.
        """
        return self.load()

    def export_json(self) -> str:
        """Exports validated configuration as redacted JSON.

        Returns:
            Redacted JSON configuration content.
        """
        return self._loader.dump(self._safe_mapping(), ConfigurationFormat.JSON)

    def export_yaml(self) -> str:
        """Exports validated configuration as redacted YAML.

        Returns:
            Redacted YAML configuration content.
        """
        return self._loader.dump(self._safe_mapping(), ConfigurationFormat.YAML)

    def _build_settings(self) -> ApplicationSettings:
        try:
            values = deep_merge(
                self._loader.load_file(self._config_path),
                self._loader.load_dotenv(self._env_file),
                self._loader.load_environment(self._environment),
                self._overrides,
            )
            return ApplicationSettings.model_validate(values)
        except PydanticValidationError as error:
            messages = tuple(
                f"{'.'.join(str(item) for item in issue['loc'])}: {issue['msg']}"
                for issue in error.errors()
            )
            raise ValidationError(messages) from error
        except ConfigurationError:
            raise
        except (TypeError, ValueError) as error:
            raise ValidationError((str(error),)) from error

    def _safe_mapping(self) -> dict[str, Any]:
        return self._redact(self.load())

    def _redact(self, value: Any) -> Any:
        if isinstance(value, SecretStr):
            return REDACTED_SECRET_VALUE
        if isinstance(value, BaseModel):
            return {
                field_name: self._redact(getattr(value, field_name))
                for field_name in value.__class__.model_fields
            }
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, AnyUrl):
            return str(value)
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, Mapping):
            return {key: self._redact(item) for key, item in value.items()}
        if isinstance(value, tuple | list):
            return [self._redact(item) for item in value]
        return value

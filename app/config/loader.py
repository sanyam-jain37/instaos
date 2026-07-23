"""Configuration source loading and deterministic merge utilities."""

import json
import os
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml
from dotenv import dotenv_values

from app.config.exceptions import InvalidConfiguration, MissingConfiguration


ENVIRONMENT_PREFIX = "INSTAOS_"
NESTED_KEY_DELIMITER = "__"
JSON_OPENING_CHARACTERS = frozenset(("[", "{"))


class ConfigurationFormat(str, Enum):
    """Supported persisted configuration formats."""

    JSON = "json"
    YAML = "yaml"


CONFIGURATION_SUFFIXES = MappingProxyType(
    {
        ".json": ConfigurationFormat.JSON,
        ".yaml": ConfigurationFormat.YAML,
        ".yml": ConfigurationFormat.YAML,
    }
)


def deep_merge(*sources: Mapping[str, Any]) -> dict[str, Any]:
    """Merges mappings from lowest to highest precedence without mutation.

    Args:
        *sources: Mapping sources ordered from lowest to highest precedence.

    Returns:
        A new recursively merged mapping.
    """
    merged: dict[str, Any] = {}
    for source in sources:
        for key, value in source.items():
            existing = merged.get(key)
            if isinstance(existing, Mapping) and isinstance(value, Mapping):
                merged[key] = deep_merge(existing, value)
            else:
                merged[key] = value
    return merged


class ConfigurationLoader:
    """Loads JSON, YAML, dotenv, and environment configuration mappings."""

    def load_file(self, path: Path | None) -> dict[str, Any]:
        """Loads a JSON or YAML mapping from an optional configuration file.

        Args:
            path: Explicit JSON or YAML file path, or ``None`` to skip it.

        Returns:
            Parsed configuration mapping.

        Raises:
            MissingConfiguration: If an explicit path does not exist.
            InvalidConfiguration: If the source has an unsupported format or
                does not contain a mapping.
        """
        if path is None:
            return {}
        if not path.is_file():
            raise MissingConfiguration(f"Configuration file does not exist: {path}")

        configuration_format = self._format_for_path(path)
        try:
            with path.open(encoding="utf-8") as configuration_file:
                if configuration_format is ConfigurationFormat.JSON:
                    loaded = json.load(configuration_file)
                else:
                    loaded = yaml.safe_load(configuration_file)
        except (json.JSONDecodeError, yaml.YAMLError) as error:
            raise InvalidConfiguration(
                f"Unable to parse configuration file: {path}"
            ) from error

        if loaded is None:
            return {}
        if not isinstance(loaded, Mapping):
            raise InvalidConfiguration("Configuration files must contain a mapping.")
        return dict(loaded)

    def load_dotenv(self, path: Path | None) -> dict[str, Any]:
        """Loads InstaOS-prefixed values from an optional dotenv file.

        Args:
            path: Dotenv file path, or ``None`` to disable dotenv loading.

        Returns:
            Nested configuration mapping extracted from the dotenv file.
        """
        if path is None or not path.is_file():
            return {}
        values = dotenv_values(path)
        return self._environment_mapping(values)

    def load_environment(self, values: Mapping[str, str] | None = None) -> dict[str, Any]:
        """Loads InstaOS-prefixed values from an environment mapping.

        Args:
            values: Environment mapping. Uses the process environment when absent.

        Returns:
            Nested configuration mapping extracted from environment values.
        """
        return self._environment_mapping(os.environ if values is None else values)

    def dump(self, data: Mapping[str, Any], configuration_format: ConfigurationFormat) -> str:
        """Serializes a safe configuration mapping.

        Args:
            data: Configuration data with secrets already redacted.
            configuration_format: Target serialization format.

        Returns:
            Serialized configuration content.
        """
        if configuration_format is ConfigurationFormat.JSON:
            return json.dumps(data, indent=2, sort_keys=True) + "\n"
        return yaml.safe_dump(dict(data), sort_keys=False)

    def format_for_path(self, path: Path) -> ConfigurationFormat:
        """Determines configuration format from a path suffix.

        Args:
            path: Configuration path.

        Returns:
            Configuration format associated with the path suffix.
        """
        return self._format_for_path(path)

    def _format_for_path(self, path: Path) -> ConfigurationFormat:
        configuration_format = CONFIGURATION_SUFFIXES.get(path.suffix.lower())
        if configuration_format is None:
            supported = ", ".join(sorted(CONFIGURATION_SUFFIXES))
            raise InvalidConfiguration(
                f"Unsupported configuration format for {path}. Use: {supported}."
            )
        return configuration_format

    def _environment_mapping(
        self,
        values: Mapping[str, str | None],
    ) -> dict[str, Any]:
        mapping: dict[str, Any] = {}
        for key, value in values.items():
            if value is None or not key.upper().startswith(ENVIRONMENT_PREFIX):
                continue

            path = key[len(ENVIRONMENT_PREFIX):].lower().split(NESTED_KEY_DELIMITER)
            if not all(path):
                raise InvalidConfiguration(
                    f"Environment variable has an invalid nested path: {key}"
                )
            self._set_nested(mapping, path, self._decode_environment_value(value))
        return mapping

    @staticmethod
    def _decode_environment_value(value: str) -> Any:
        stripped_value = value.strip()
        if stripped_value[:1] in JSON_OPENING_CHARACTERS:
            try:
                return json.loads(stripped_value)
            except json.JSONDecodeError:
                return value
        return value

    @staticmethod
    def _set_nested(mapping: dict[str, Any], path: list[str], value: Any) -> None:
        current = mapping
        for key in path[:-1]:
            nested = current.get(key)
            if nested is None:
                nested = {}
                current[key] = nested
            if not isinstance(nested, dict):
                raise InvalidConfiguration(
                    f"Configuration path conflicts at nested key: {key}"
                )
            current = nested
        current[path[-1]] = value

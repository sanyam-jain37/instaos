import json
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from app.config import (
    ConfigManager,
    InvalidConfiguration,
    MissingConfiguration,
    ValidationError,
)
from app.config.loader import ConfigurationFormat, ConfigurationLoader, deep_merge


SECRET_TOKEN = "a-secure-test-token"
API_URL = "https://graph.instagram.example/v1"


def write_json(path: Path, data: dict[str, object]) -> Path:
    """Writes JSON test configuration content."""
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def write_yaml(path: Path, data: dict[str, object]) -> Path:
    """Writes YAML test configuration content."""
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def account(account_id: str = "account-1", username: str = "instaos") -> dict[str, str]:
    """Builds a valid Instagram account configuration mapping."""
    return {
        "account_id": account_id,
        "username": username,
        "access_token": SECRET_TOKEN,
        "api_base_url": API_URL,
    }


@pytest.mark.parametrize(
    ("suffix", "writer"),
    [(".json", write_json), (".yaml", write_yaml)],
)
def test_loads_json_and_yaml_configuration(
    tmp_path: Path,
    suffix: str,
    writer: Callable[[Path, dict[str, object]], Path],
) -> None:
    config_path = tmp_path / f"instaos{suffix}"
    writer(config_path, {"application": {"api_port": 9_001}})

    settings = ConfigManager(config_path=config_path, env_file=None).load()

    assert settings.application.api_port == 9_001


def test_runtime_precedence_over_environment_dotenv_and_file(tmp_path: Path) -> None:
    config_path = write_json(
        tmp_path / "config.json",
        {"application": {"api_port": 9_001}},
    )
    env_path = tmp_path / ".env"
    env_path.write_text("INSTAOS_APPLICATION__API_PORT=9002\n", encoding="utf-8")

    settings = ConfigManager(
        config_path=config_path,
        env_file=env_path,
        environment={"INSTAOS_APPLICATION__API_PORT": "9003"},
        overrides={"application": {"api_port": 9_004}},
    ).load()

    assert settings.application.api_port == 9_004


def test_load_caches_and_reload_reparses_sources(tmp_path: Path) -> None:
    config_path = write_json(
        tmp_path / "config.json",
        {"application": {"api_port": 9_001}},
    )
    manager = ConfigManager(config_path=config_path, env_file=None)
    initial = manager.load()
    write_json(config_path, {"application": {"api_port": 9_002}})

    assert manager.load() is initial
    assert manager.reload().application.api_port == 9_002


def test_validate_returns_cached_settings() -> None:
    manager = ConfigManager(env_file=None)

    assert manager.validate() is manager.load()


def test_exports_and_saves_redacted_secrets(tmp_path: Path) -> None:
    manager = ConfigManager(
        env_file=None,
        overrides={
            "instagram": {"enabled": True, "accounts": [account()]},
            "ai_providers": {
                "providers": [
                    {
                        "name": "primary",
                        "model": "model-1",
                        "enabled": True,
                        "api_key": SECRET_TOKEN,
                    }
                ]
            },
        },
    )

    exported_json = manager.export_json()
    exported_yaml = manager.export_yaml()
    saved_path = manager.save(tmp_path / "export.yaml")

    assert SECRET_TOKEN not in exported_json
    assert SECRET_TOKEN not in exported_yaml
    assert "********" in exported_json
    assert json.loads(exported_json)["instagram"]["accounts"][0]["access_token"] == "********"
    assert saved_path.read_text(encoding="utf-8") == exported_yaml


def test_save_infers_json_format(tmp_path: Path) -> None:
    saved_path = ConfigManager(env_file=None).save(tmp_path / "export.json")

    assert json.loads(saved_path.read_text(encoding="utf-8"))["application"]["name"] == "InstaOS"


def test_redacted_export_cannot_be_reused_as_a_secret() -> None:
    manager = ConfigManager(
        env_file=None,
        overrides={"instagram": {"enabled": True, "accounts": [account()]}},
    )
    exported = json.loads(manager.export_json())

    with pytest.raises(ValidationError, match="Secret values"):
        ConfigManager(env_file=None, overrides=exported).load()


def test_invalid_port_raises_sanitized_validation_error(tmp_path: Path) -> None:
    config_path = write_json(
        tmp_path / "invalid.json",
        {"application": {"api_port": 70_000}},
    )

    with pytest.raises(ValidationError, match="api_port"):
        ConfigManager(config_path=config_path, env_file=None).load()


def test_duplicate_instagram_accounts_raise_validation_error() -> None:
    with pytest.raises(ValidationError, match="Duplicate account ID"):
        ConfigManager(
            env_file=None,
            overrides={
                "instagram": {
                    "accounts": [account(), account(username="different-name")]
                }
            },
        ).load()


def test_invalid_directory_raises_validation_error(tmp_path: Path) -> None:
    file_path = tmp_path / "not-a-directory"
    file_path.write_text("content", encoding="utf-8")

    with pytest.raises(ValidationError, match="data_directory"):
        ConfigManager(
            env_file=None,
            overrides={"application": {"data_directory": str(file_path)}},
        ).load()


def test_missing_explicit_configuration_raises_error(tmp_path: Path) -> None:
    with pytest.raises(MissingConfiguration):
        ConfigManager(config_path=tmp_path / "missing.yaml", env_file=None).load()


def test_invalid_configuration_format_raises_error(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("key = 'value'", encoding="utf-8")

    with pytest.raises(InvalidConfiguration, match="Unsupported configuration format"):
        ConfigManager(config_path=config_path, env_file=None).load()


def test_invalid_json_raises_error(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.json"
    config_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(InvalidConfiguration, match="Unable to parse"):
        ConfigManager(config_path=config_path, env_file=None).load()


def test_loader_merges_nested_mappings_without_mutating_sources() -> None:
    low_priority = {"application": {"debug": False, "api_port": 8_000}}
    high_priority = {"application": {"api_port": 9_000}}

    merged = deep_merge(low_priority, high_priority)

    assert merged == {"application": {"debug": False, "api_port": 9_000}}
    assert low_priority["application"]["api_port"] == 8_000


def test_loader_reads_nested_environment_and_json_lists() -> None:
    loader = ConfigurationLoader()

    values = loader.load_environment(
        {
            "INSTAOS_APPLICATION__API_PORT": "9001",
            "INSTAOS_PUBLISHERS__PUBLISHERS": '[{"name":"x","publisher_type":"test"}]',
            "UNRELATED_VALUE": "ignored",
        }
    )

    assert values["application"]["api_port"] == "9001"
    assert values["publishers"]["publishers"][0]["name"] == "x"


def test_loader_dump_supports_explicit_formats() -> None:
    loader = ConfigurationLoader()

    assert '"name": "InstaOS"' in loader.dump(
        {"name": "InstaOS"},
        ConfigurationFormat.JSON,
    )
    assert "name: InstaOS" in loader.dump(
        {"name": "InstaOS"},
        ConfigurationFormat.YAML,
    )

"""Strongly typed models for InstaOS configuration."""

from enum import Enum
from pathlib import Path
from typing import Final, Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, SecretStr
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.validators import ensure_unique, validate_directory, validate_secret_value


MAXIMUM_PORT = 65_535
MINIMUM_PORT = 1
DEFAULT_API_PORT = 8_000
DEFAULT_SCHEDULER_POLL_SECONDS = 60
DEFAULT_MAX_CONCURRENT_JOBS = 4
DEFAULT_APPLICATION_NAME = "InstaOS"
EnvironmentName = Literal[
    "development",
    "test",
    "staging",
    "production",
]

DEFAULT_ENVIRONMENT: Final[EnvironmentName] = "development"
DEFAULT_TIMEZONE = "UTC"
DEFAULT_DATABASE_URL = "sqlite:///data/instaos.db"
DEFAULT_GOOGLE_ROOT_FOLDER = "root"
DEFAULT_LOG_DIRECTORY = Path("logs")
DEFAULT_STORAGE_DIRECTORY = Path("data/assets")
ENVIRONMENT_PREFIX = "INSTAOS_"
ENVIRONMENT_NESTED_DELIMITER = "__"


class ConfigurationModel(BaseModel):
    """Base model that rejects unknown values and prevents mutation."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class LogLevel(str, Enum):
    """Supported application log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StorageBackend(str, Enum):
    """Supported asset storage backends."""

    LOCAL = "local"
    S3 = "s3"
    GOOGLE_DRIVE = "google_drive"

class ApplicationConfig(ConfigurationModel):
    """Application identity and process-level configuration."""

    name: str = Field(default=DEFAULT_APPLICATION_NAME, min_length=1)
    environment: EnvironmentName = DEFAULT_ENVIRONMENT
    debug: bool = False
    api_host: str = Field(default="127.0.0.1", min_length=1)
    api_port: int = Field(
        default=DEFAULT_API_PORT,
        ge=MINIMUM_PORT,
        le=MAXIMUM_PORT,
    )
    data_directory: Path = Path("data")

    @field_validator("data_directory")
    @classmethod
    def validate_data_directory(cls, value: Path) -> Path:
        """Validates the application data directory."""
        return validate_directory(value)


class DatabaseConfig(ConfigurationModel):
    """Database connectivity settings."""

    url: str = Field(default=DEFAULT_DATABASE_URL, min_length=1)
    echo_sql: bool = False

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        """Validates a supported database URL scheme."""
        supported_schemes = ("sqlite://", "postgresql://", "mysql://")
        if not value.startswith(supported_schemes):
            raise ValueError("Database URL must use sqlite, postgresql, or mysql.")
        return value


class GoogleDriveConfig(ConfigurationModel):
    """Google Drive source configuration."""

    enabled: bool = True
    credentials_path: Path | None = None
    token_path: Path | None = None
    root_folder_id: str = Field(default=DEFAULT_GOOGLE_ROOT_FOLDER, min_length=1)
    read_only: bool = True


class InstagramAccountConfig(ConfigurationModel):
    """Configuration for one Instagram publishing account."""

    account_id: str = Field(min_length=1)
    username: str = Field(min_length=1)
    access_token: SecretStr
    api_base_url: AnyHttpUrl
    enabled: bool = True

    @field_validator("access_token", mode="before")
    @classmethod
    def validate_access_token(cls, value: str | SecretStr | None) -> str | None:
        """Validates the account access token without exposing it."""
        return validate_secret_value(value)


class InstagramConfig(ConfigurationModel):
    """Instagram publisher configuration."""

    enabled: bool = False
    accounts: tuple[InstagramAccountConfig, ...] = ()

    @model_validator(mode="after")
    def validate_accounts(self) -> "InstagramConfig":
        """Validates unique Instagram account identifiers and usernames."""
        ensure_unique((account.account_id for account in self.accounts), "account ID")
        ensure_unique((account.username for account in self.accounts), "account username")
        if self.enabled and not self.accounts:
            raise ValueError("Instagram requires at least one account when enabled.")
        return self


class SchedulerConfig(ConfigurationModel):
    """Background scheduling configuration."""

    enabled: bool = False
    timezone: str = Field(default=DEFAULT_TIMEZONE, min_length=1)
    poll_interval_seconds: int = Field(
        default=DEFAULT_SCHEDULER_POLL_SECONDS,
        ge=1,
    )
    max_concurrent_jobs: int = Field(default=DEFAULT_MAX_CONCURRENT_JOBS, ge=1)


class LoggingConfig(ConfigurationModel):
    """Application logging configuration."""

    level: LogLevel = LogLevel.INFO
    directory: Path = DEFAULT_LOG_DIRECTORY
    json_output: bool = True

    @field_validator("directory")
    @classmethod
    def validate_log_directory(cls, value: Path) -> Path:
        """Validates the configured log directory."""
        return validate_directory(value)


class AIProviderConfig(ConfigurationModel):
    """Configuration for one AI provider connection."""

    name: str = Field(min_length=1)
    model: str = Field(min_length=1)
    api_key: SecretStr | None = None
    base_url: AnyHttpUrl | None = None
    enabled: bool = False

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, value: str | SecretStr | None) -> str | None:
        """Validates an API key without exposing it."""
        return validate_secret_value(value)

    @model_validator(mode="after")
    def validate_enabled_provider(self) -> "AIProviderConfig":
        """Requires a secret when an AI provider is enabled."""
        if self.enabled and self.api_key is None:
            raise ValueError("An enabled AI provider requires an API key.")
        return self


class AIProvidersConfig(ConfigurationModel):
    """AI provider pipeline configuration."""

    providers: tuple[AIProviderConfig, ...] = ()

    @model_validator(mode="after")
    def validate_provider_names(self) -> "AIProvidersConfig":
        """Validates unique AI provider names."""
        ensure_unique((provider.name for provider in self.providers), "AI provider")
        return self


class StorageConfig(ConfigurationModel):
    """Asset storage configuration supporting local and cloud backends."""

    backend: StorageBackend = StorageBackend.LOCAL
    local_directory: Path = DEFAULT_STORAGE_DIRECTORY
    bucket: str | None = None
    region: str | None = None

    @field_validator("local_directory")
    @classmethod
    def validate_local_directory(cls, value: Path) -> Path:
        """Validates the local asset storage directory."""
        return validate_directory(value)

    @model_validator(mode="after")
    def validate_backend_requirements(self) -> "StorageConfig":
        """Validates backend-specific required values."""
        if self.backend is StorageBackend.S3 and not self.bucket:
            raise ValueError("S3 storage requires a bucket.")
        return self


class PublisherConfig(ConfigurationModel):
    """Configuration for a future publishing platform integration."""

    name: str = Field(min_length=1)
    publisher_type: str = Field(min_length=1)
    enabled: bool = False
    endpoint: AnyHttpUrl | None = None


class PublishersConfig(ConfigurationModel):
    """Future social and distribution publisher configuration."""

    publishers: tuple[PublisherConfig, ...] = ()

    @model_validator(mode="after")
    def validate_publisher_names(self) -> "PublishersConfig":
        """Validates unique publisher names."""
        ensure_unique((publisher.name for publisher in self.publishers), "publisher")
        return self


class ApplicationSettings(BaseSettings):
    """Complete immutable configuration for an InstaOS process."""

    model_config = SettingsConfigDict(
        env_prefix=ENVIRONMENT_PREFIX,
        env_nested_delimiter=ENVIRONMENT_NESTED_DELIMITER,
        env_ignore_empty=True,
        extra="forbid",
        frozen=True,
    )

    application: ApplicationConfig = Field(default_factory=ApplicationConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    google_drive: GoogleDriveConfig = Field(default_factory=GoogleDriveConfig)
    instagram: InstagramConfig = Field(default_factory=InstagramConfig)
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ai_providers: AIProvidersConfig = Field(default_factory=AIProvidersConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    publishers: PublishersConfig = Field(default_factory=PublishersConfig)

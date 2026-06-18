import json
from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Seamless Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = False

    # ALLOWED_ORIGINS เก็บเป็น str เพื่อหลีกเลี่ยง pydantic-settings json.loads()
    # รับได้ทั้งรูปแบบ: "http://localhost:5173,https://example.com"
    # หรือ JSON: '["http://localhost:5173"]'
    allowed_origins: str = "http://localhost:5173"

    # Database
    db_mode: Literal["ssh", "direct"] = "direct"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ic_finance"
    db_user: str = "postgres"
    db_password: str = ""
    db_pool_min_size: int = 2
    db_pool_max_size: int = 20
    db_connect_timeout: int = 10

    # SSH Tunnel
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_username: str = ""
    ssh_key_path: str = ""
    ssh_password: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl_default: int = 300
    redis_ttl_master: int = 3600
    redis_ttl_coordinator: int = 600

    # Security
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_seconds: int = 3600
    encryption_key: str = ""

    # Microsoft Entra ID
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_authority: str = ""

    # Draft mode
    draft_mode: bool = True

    # Rate Limiting
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "10/minute"

    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"
    sentry_dsn: str = ""

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if not self.debug and self.jwt_secret_key == "change-me-in-production":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from the default value "
                "before running in production (DEBUG=False)"
            )
        return self

    @field_validator("sentry_dsn", "encryption_key", "azure_tenant_id", "azure_client_id", mode="before")
    @classmethod
    def strip_optional_str(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v

    # Dev: local users
    auth_users_json: str = "[]"

    def get_allowed_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS — รองรับทั้ง comma-separated และ JSON array"""
        v = self.allowed_origins.strip()
        if not v:
            return ["http://localhost:5173"]
        # ลอง JSON array ก่อน เช่น '["http://a.com","http://b.com"]'
        if v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(o).strip() for o in parsed if o]
            except json.JSONDecodeError:
                pass
        # Comma-separated: "http://a.com,https://b.com"
        return [o.strip() for o in v.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

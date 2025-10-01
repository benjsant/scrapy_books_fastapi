from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os
from urllib.parse import quote_plus
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError


def to_snake_case(name: str) -> str:
    """Convert kebab-case from Key Vault to snake_case Python variable."""
    return name.lower().replace("-", "_")


# Always resolve .env path relative to project root
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"  # ../../.env → root


class Settings(BaseSettings):
    # -----------------------------
    # Azure Key Vault
    # -----------------------------
    azure_key_vault_url: Optional[str] = None
    _secrets_cache: dict = {}

    # -----------------------------
    # Database config
    # -----------------------------
    db_user: Optional[str] = Field(None, alias="DB_USER")
    db_password: Optional[str] = Field(None, alias="DB_PASSWORD")
    db_host: Optional[str] = Field(None, alias="DB_HOST")
    db_name: Optional[str] = Field(None, alias="DB_NAME")
    db_port: Optional[str] = Field(None, alias="DB_PORT")

    # -----------------------------
    # Flags for main.py
    # -----------------------------
    docker_on: bool = Field(False, alias="DOCKER_ON")
    run_scrapy: bool = Field(True, alias="RUN_SCRAPY")
    run_api: bool = Field(True, alias="RUN_API")

    # -----------------------------
    # Pydantic config
    # -----------------------------
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),  # absolute path to root .env
        extra="ignore",
        populate_by_name=True,
    )

    # -----------------------------
    # Methods
    # -----------------------------
    # If I have time to use azure and postgresql 
    def load_from_key_vault(self, force_reload: bool = False) -> None:
        """Load secrets from Azure Key Vault if URL provided."""
        if not self.azure_key_vault_url:
            print("[INFO] No Key Vault URL provided. Using .env only.")
            return

        if self._secrets_cache and not force_reload:
            for key, value in self._secrets_cache.items():
                setattr(self, key, value)
            print("[INFO] Configuration loaded from cache.")
            return

        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=self.azure_key_vault_url, credential=credential)
            new_cache = {}
            for secret_props in client.list_properties_of_secrets():
                key = to_snake_case(secret_props.name)
                value = client.get_secret(secret_props.name).value
                if hasattr(self, key):
                    setattr(self, key, value)
                    new_cache[key] = value
            self._secrets_cache = new_cache
            print("[INFO] Configuration loaded from Azure Key Vault.")
        except AzureError as e:
            print(f"[WARNING] Could not load secrets from Key Vault: {e}")

    @property
    def database_url(self) -> str:
        """Return the DATABASE_URL, properly URL-encoded to avoid UTF-8 issues."""
        if all([self.db_user, self.db_password, self.db_host, self.db_port, self.db_name]):
            user = quote_plus(self.db_user)
            password = quote_plus(self.db_password)
            host = self.db_host
            port = self.db_port
            dbname = quote_plus(self.db_name)  # safe in case db name has weird chars
            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return os.getenv(
            "DATABASE_URL",
            "postgresql://books_user:books_password@localhost:5433/books_db"
        )


# -----------------------------
# Singleton instance
# -----------------------------
settings = Settings()

# Only attempt to load Key Vault if URL is provided
if settings.azure_key_vault_url:
    settings.load_from_key_vault()

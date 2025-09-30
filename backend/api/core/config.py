from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import AzureError
import os

def to_snake_case(name: str) -> str:
    """Convert kebab-case from Key Vault to snake_case Python variable."""
    return name.lower().replace("-", "_")

class Settings(BaseSettings):
    # Azure Key Vault
    azure_key_vault_url: Optional[str] = None

    # Database
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_host: Optional[str] = None
    db_name: Optional[str] = None
    db_port: Optional[str] = None

    print()
    print
    # Cache interne
    _secrets_cache: dict = {}

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def load_from_key_vault(self, force_reload: bool = False) -> None:
        """Load secrets from Azure Key Vault and convert kebab-case to snake_case."""
        if not self.azure_key_vault_url:
            print("[INFO] No Key Vault URL provided. Using .env only.")
            return

        if self._secrets_cache and not force_reload:
            for key, value in self._secrets_cache.items():
                setattr(self, key, value)
            print("[INFO] Config loaded from cache.")
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
        """Return the DATABASE_URL, preferring Key Vault values if available."""
        print(self.db_host,self.db_name, self.db_password, self.db_user,self.db_port)
        if self.db_user and self.db_password and self.db_host and self.db_port and self.db_name:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return os.getenv(
            "DATABASE_URL",
            "postgresql://books_user:books_password@localhost:5433/books_db"
        )

# Singleton
settings = Settings()
settings.load_from_key_vault()

import pytest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import AzureError
from app.core.config import Settings, to_snake_case


def test_to_snake_case():
    """Test conversion of Key Vault names to snake_case."""
    assert to_snake_case("AZURE-OPENAI-API-KEY") == "azure_openai_api_key"
    assert to_snake_case("Already_Snake") == "already_snake"
    assert to_snake_case("") == ""


def test_cors_origins_with_allowed_origins():
    """If allowed_origins is defined, it should be split correctly."""
    settings = Settings(allowed_origins="http://foo.com,http://bar.com")
    assert settings.cors_origins == ["http://foo.com", "http://bar.com"]


def test_cors_origins_without_allowed_origins():
    """If allowed_origins is None, defaults should be returned."""
    settings = Settings(allowed_origins=None)
    assert "http://localhost:3000" in settings.cors_origins
    assert "http://127.0.0.1:3000" in settings.cors_origins


def test_load_from_key_vault_no_url(capfd):
    """Should not try to load secrets if azure_key_vault_url is missing."""
    settings = Settings(azure_key_vault_url=None)
    settings.load_from_key_vault()
    out, _ = capfd.readouterr()
    assert "No Key Vault URL provided" in out


def test_load_from_key_vault_with_cache():
    """Should load secrets from cache if available and force_reload=False."""
    settings = Settings(azure_key_vault_url="https://fake-vault.vault.azure.net/")
    settings._secrets_cache = {"jamendo_client_id": "cached123"}
    settings.load_from_key_vault(force_reload=False)
    assert settings.jamendo_client_id == "cached123"


@patch("app.core.config.SecretClient")
@patch("app.core.config.DefaultAzureCredential")
def test_load_from_key_vault_success(mock_credential, mock_secret_client):
    """Should load secrets from Key Vault when available."""
    # Create a mock secret with a real .name attribute
    secret_mock = MagicMock()
    secret_mock.name = "AZURE-OPENAI-API-KEY"
    fake_secret_props = [secret_mock]

    fake_client = MagicMock()
    fake_client.list_properties_of_secrets.return_value = fake_secret_props
    fake_client.get_secret.return_value.value = "supersecret"

    mock_secret_client.return_value = fake_client

    settings = Settings(azure_key_vault_url="https://fake-vault.vault.azure.net/")
    settings.load_from_key_vault(force_reload=True)

    assert settings.azure_openai_api_key == "supersecret"
    assert "azure_openai_api_key" in settings._secrets_cache


@patch("app.core.config.SecretClient", side_effect=AzureError("boom"))
@patch("app.core.config.DefaultAzureCredential")
def test_load_from_key_vault_failure(mock_credential, mock_secret_client, capfd):
    """Should catch AzureError and log a warning instead of crashing."""
    settings = Settings(azure_key_vault_url="https://fake-vault.vault.azure.net/")
    settings.load_from_key_vault(force_reload=True)
    out, _ = capfd.readouterr()
    assert "Could not load secrets from Key Vault" in out

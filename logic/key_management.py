from qgis.core import QgsApplication, QgsAuthMethodConfig
from typing import Optional, TypedDict


class LoggedInUser(TypedDict):
    url: str
    api_key: str


def fetch_config_id() -> Optional[str]:
    """Fetch the configuration ID for Lobsta."""
    auth_mgr = QgsApplication.authManager()
    for config_id in auth_mgr.configIds():
        auth_config = QgsAuthMethodConfig()
        auth_mgr.loadAuthenticationConfig(config_id, auth_config, full=True)
        if auth_config.name() == "Lobsta-Website":
            return config_id
    return None


def fetch_auth_config() -> Optional[LoggedInUser]:
    """Fetch the authentication configuration for Lobsta."""
    auth_mgr = QgsApplication.authManager()
    config_id = fetch_config_id()
    if config_id:
        auth_config = QgsAuthMethodConfig()
        auth_mgr.loadAuthenticationConfig(config_id, auth_config, full=True)
        return {
            "url": auth_config.uri(),
            "api_key": auth_config.config("X-Redmine-API-Key"),
        }
    return None


def store_auth_config(url: str, username: str, password: str, api_key: str) -> None:
    """Store the authentication configuration for Lobsta."""
    auth_mgr = QgsApplication.authManager()

    http_config = QgsAuthMethodConfig()
    existing_config_id = fetch_config_id()
    if existing_config_id:
        auth_mgr.loadAuthenticationConfig(existing_config_id, http_config, full=True)

    http_config.setName("Lobsta-Website")
    http_config.setMethod("APIHeader")
    http_config.setUri(url)
    http_config.setConfig("X-Redmine-API-Key", api_key)

    assert http_config.isValid()

    auth_mgr.storeAuthenticationConfig(http_config, overwrite=True)


def delete_auth_config() -> None:
    """Delete the authentication configuration for Lobsta."""
    auth_mgr = QgsApplication.authManager()
    config_id = fetch_config_id()
    if config_id:
        auth_config = QgsAuthMethodConfig()
        auth_mgr.loadAuthenticationConfig(config_id, auth_config, full=True)
        auth_config.setConfig("X-Redmine-API-Key", "")
        auth_mgr.storeAuthenticationConfig(auth_config, overwrite=True)

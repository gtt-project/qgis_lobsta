import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, TypedDict


class UserInformation(TypedDict):
    login: str
    api_key: str


class User(TypedDict):
    user: UserInformation


def authenticate(base_url: str, username: str, password: str) -> Optional[User]:
    redmine_entrypoint = f"{base_url}/users/current.json"
    response = requests.get(redmine_entrypoint, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        json = response.json()
        return {
            "user": {"login": json["user"]["login"], "api_key": json["user"]["api_key"]}
        }
    else:
        return None


def authenticate_via_api(base_url: str, api_key: str) -> Optional[User]:
    redmine_entrypoint = f"{base_url}/users/current.json"
    headers = {"X-Redmine-API-Key": api_key}
    response = requests.get(redmine_entrypoint, headers=headers)
    if response.status_code == 200:
        json = response.json()
        return {
            "user": {"login": json["user"]["login"], "api_key": json["user"]["api_key"]}
        }
    else:
        return None

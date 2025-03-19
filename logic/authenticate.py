import requests
from requests.auth import HTTPBasicAuth
from typing import Optional

def authenticate(base_url: str, username: str, password: str) -> Optional[str]:
    redmine_entrypoint = f"{base_url}/users/current.json"
    response = requests.get(redmine_entrypoint, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        return response.json()
    else:
        return None
import requests
from typing import Optional, TypedDict


class Project(TypedDict):
    id: int
    name: str
    identifier: str
    description: str
    homepage: Optional[str]
    status: int
    is_public: bool
    inherit_members: bool
    created_on: str
    updated_on: str


def fetch_projects(base_url: str, api_key: str) -> Optional[list[Project]]:
    """
    Fetch all projects from the Redmine server.
    """
    redmine_entrypoint = f"{base_url}/projects.json"
    headers = {"X-Redmine-API-Key": api_key}
    response = requests.get(redmine_entrypoint, headers=headers)

    if response.status_code == 200:
        json = response.json()
        return json["projects"]
    else:
        return []

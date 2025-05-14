import requests
from typing import Optional
# Issues have a different structure for each project, so we don't define a TypedDict for them.


def fetch_issues(
    base_url: str,
    api_key: str,
    project_id: int,
    limit: int,
    query_id: Optional[int] = None,
) -> Optional[list[dict]]:
    """
    Fetch issues from the Redmine server.
    """
    redmine_entrypoint = f"{base_url}/issues.json"
    headers = {"X-Redmine-API-Key": api_key}
    params = {"project_id": project_id, "offset": 0, "limit": limit}
    if query_id:
        params["query_id"] = query_id

    response = requests.get(redmine_entrypoint, headers=headers, params=params)

    if response.status_code == 200:
        json = response.json()
        return json["issues"]
    else:
        return []

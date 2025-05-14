import requests
from typing import Optional, TypedDict


class Query(TypedDict):
    id: int
    name: str
    is_public: bool
    project_id: Optional[int]


def fetch_queries(
    base_url: str, api_key: str, project_id: int
) -> Optional[list[Query]]:
    """
    Fetch all custom queries from the Redmine server.
    """
    redmine_entrypoint = f"{base_url}/queries.json"
    headers = {"X-Redmine-API-Key": api_key}
    response = requests.get(redmine_entrypoint, headers=headers)

    if response.status_code == 200:
        json = response.json()
        results = []
        if "queries" in json:
            queries = json["queries"]
            for query in queries:
                if query["project_id"] is None or query["project_id"] == project_id:
                    results.append(
                        Query(
                            id=query["id"],
                            name=query["name"],
                            is_public=query["is_public"],
                            project_id=query["project_id"],
                        )
                    )
        return results
    else:
        return []

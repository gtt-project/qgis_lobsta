import requests
import tempfile
import json


def fetch_geojsons(
    temp_dir: tempfile.TemporaryDirectory, base_url: str, api_key: str, ids: list[int]
) -> list[str]:
    """
    Fetch geojsons from the Redmine server.
    """
    # Create a temporary directory to store the geojson files
    geojsons_path = []

    for id in ids:
        redmine_entrypoint = f"{base_url}/issues/{id}.geojson"
        headers = {"X-Redmine-API-Key": api_key}
        response = requests.get(redmine_entrypoint, headers=headers)
        if response.status_code == 200:
            # Save the geojson to a temporary file
            geojson_path = f"{temp_dir.name}/{id}.geojson"
            with open(geojson_path, "w") as f:
                # Append the URL of the geojson to the file
                geojson = response.json()
                geojson["properties"]["upstream_url"] = redmine_entrypoint
                json.dump(geojson, f)
            geojsons_path.append(geojson_path)
        else:
            print(f"Failed to fetch geojson for issue {id}: {response.status_code}")
            continue
    return geojsons_path

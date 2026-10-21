import re

import requests

HEADERS = {"user-agent": "Mozilla/5.0"}


def reference_ids(url, resource):
    match = re.search(rf"/leagues/(\d+)/{resource}/(\d+)(?:/|$)", url)
    if match is None:
        raise ValueError(f"Invalid {resource} reference: {url}")
    return int(match.group(1)), int(match.group(2))


def get_json(url, not_found_error):
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code == 404:
        raise not_found_error(f"Not found: {url}")
    response.raise_for_status()
    return response.json()


def collection_refs(url, not_found_error):
    references = []
    page = 1
    while True:
        page_url = url if page == 1 else f"{url}?page={page}"
        data = get_json(page_url, not_found_error)
        references.extend(item["$ref"] for item in data.get("items", []))
        if page >= data.get("pageCount", 1):
            return references
        page += 1

"""Shared HTTP and reference helpers for the ESPN core API."""

import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

HEADERS = {"user-agent": "Mozilla/5.0"}
TIMEOUT = 30

# ESPN's core API intermittently answers "503 Backend fetch failed". A player's
# major teams take one request each, so without retries one blip fails the call.
# raise_on_status=False hands back the last response after the retries, so
# callers keep their own 404 and raise_for_status handling.
_RETRY = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(500, 502, 503, 504),
    allowed_methods=("GET",),
    raise_on_status=False,
)
_SESSION = requests.Session()
_SESSION.mount("http://", HTTPAdapter(max_retries=_RETRY))
_SESSION.mount("https://", HTTPAdapter(max_retries=_RETRY))


def http_get(url, headers=None):
    """GET ``url`` with the shared timeout and retry policy."""
    return _SESSION.get(url, headers=headers or HEADERS, timeout=TIMEOUT)


def reference_ids(url, resource):
    """Return the (series_id, resource_id) pair from a core API reference URL."""
    match = re.search(rf"/leagues/(\d+)/{resource}/(\d+)(?:/|$)", url)
    if match is None:
        raise ValueError(f"Invalid {resource} reference: {url}")
    return int(match.group(1)), int(match.group(2))


def get_json(url, not_found_error):
    """Return the JSON at ``url``; raise ``not_found_error`` on 404."""
    response = http_get(url)
    if response.status_code == 404:
        raise not_found_error(f"Not found: {url}")
    response.raise_for_status()
    return response.json()


def collection_refs(url, not_found_error):
    """Return every ``$ref`` in a paginated core API collection."""
    references = []
    page = 1
    while True:
        page_url = url if page == 1 else f"{url}?page={page}"
        data = get_json(page_url, not_found_error)
        references.extend(item["$ref"] for item in data.get("items", []))
        if page >= data.get("pageCount", 1):
            return references
        page += 1

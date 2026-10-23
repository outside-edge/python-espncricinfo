import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name):
    with (FIXTURE_DIR / name).open() as f:
        return json.load(f)


def load_fixture_text(name):
    return (FIXTURE_DIR / name).read_text()


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run integration tests against live ESPN API",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as requiring live ESPN API (run with --live)"
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--live"):
        skip_live = pytest.mark.skip(reason="Pass --live to run integration tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_live)

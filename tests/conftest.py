import json
import os
import pytest
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name):
    with open(FIXTURE_DIR / name) as f:
        return json.load(f)


def load_fixture_text(name):
    with open(FIXTURE_DIR / name) as f:
        return f.read()


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

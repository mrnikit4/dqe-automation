import pytest
import pandas as pd
import csv
from pathlib import Path

# Fixture to read the CSV file
@pytest.fixture(scope="session")
def csv_reader():
    file_path = Path("../src/data/data.csv")
    assert file_path.exists(), "CSV file does not exist"

    with open(file_path, "r") as csv_file:
        yield csv.DictReader(csv_file)

# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def actual_schema(csv_reader):
    return csv_reader["headers"]

@pytest.fixture(scope="session")
def expected_schema():
    return ["id", "name", "age", "email", "is_active"]

@pytest.fixture(scope="session")
def schema_validation(actual_schema, expected_schema):
    assert actual_schema == expected_schema


# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)
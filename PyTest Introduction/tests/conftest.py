import pytest
import csv
from pathlib import Path


@pytest.fixture(scope="session")
def path_to_file():
    return Path(__file__).parent.parent / "src" / "data" / "data.csv"


# Fixture to read the CSV file
@pytest.fixture(scope="session")
def csv_reader(path_to_file):
    assert path_to_file.exists(), "CSV file does not exist"

    with open(path_to_file, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


# Fixture to validate the schema of the file
@pytest.fixture(scope="session")
def actual_schema(csv_reader):
    return list(csv_reader[0].keys())

@pytest.fixture(scope="session")
def expected_schema():
    return ["id", "name", "age", "email", "is_active"]

@pytest.fixture(scope="session")
def schema_validation(actual_schema, expected_schema):
    assert actual_schema == expected_schema, f"Schema mismatch! Expected {expected_schema}, but got {actual_schema}"
    return True

# Pytest hook to mark unmarked tests with a custom mark
def pytest_collection_modifyitems(items):
    for item in items:
        if not list(item.iter_markers()):
            item.add_marker(pytest.mark.unmarked)
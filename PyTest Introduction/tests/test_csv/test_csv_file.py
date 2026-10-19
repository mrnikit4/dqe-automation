import pytest
import re
import csv
from pathlib import Path


def test_file_not_empty(csv_reader):
    assert next(csv_reader, None) is not None, "CSV file does not contain data"


@pytest.mark.validate_csv
def test_validate_schema(csv_reader):
    allowed_headers = ['id', 'name', 'age', 'email', 'is_active']
    assert csv_reader.fieldnames == allowed_headers, "CSV file does not contain correct headers"


@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_column_valid(csv_reader):
    for row in csv_reader:
        assert 0 < int(row['age']) < 100


@pytest.mark.validate_csv
def test_email_column_valid(csv_reader):
    email_pattern = r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$"

    for row in csv_reader:
        assert re.match(email_pattern, row['email']) is not None, "Invalid Email"


@pytest.mark.validate_csv
@pytest.mark.xfail
def test_duplicates(csv_reader):
    ids = []
    for row in csv_reader:
        ids.append(row['id'])

    assert len(ids) == len(set(ids)), "Duplicate IDs"


@pytest.mark.parametrize("user_id, expected_value",[
    ("1", "False"),
    ("2", "True")
])
def test_active_players(csv_reader, user_id, expected_value):
    for row in csv_reader:
        if row['id'] == user_id:
            assert row["is_active"] == expected_value


def test_active_player(csv_reader):
    for row in csv_reader:
        if row['id'] == 2:
            assert row["is_active"] == True
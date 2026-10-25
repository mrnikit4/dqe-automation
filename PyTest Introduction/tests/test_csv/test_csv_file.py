import pytest
import re


def test_file_not_empty(csv_reader):
    assert len(csv_reader) > 0, "CSV file does not contain data"


@pytest.mark.validate_csv
def test_validate_schema(csv_reader, schema_validation):
    assert schema_validation is True, "CSV file does not contain correct headers"


def test_inspect_csv(csv_reader):
    print("\n--- CSV CONTENT DEBUG ---")
    print(csv_reader)
    print("------------------------")
    assert len(csv_reader) > 0

@pytest.mark.validate_csv
@pytest.mark.skip
def test_age_column_valid(csv_reader):
    for row in csv_reader:
        age = int(row['age'])
        assert 0 <= age <= 100, f"Invalid age value found: {age} for user {row.get('name')}"


@pytest.mark.validate_csv
def test_email_column_valid(csv_reader):
    email_pattern = r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$"

    for row in csv_reader:
        assert re.match(email_pattern, row['email']) is not None, "Invalid Email"


@pytest.mark.validate_csv
@pytest.mark.xfail
def test_duplicates(csv_reader):
    seen_rows = set()
    duplicates_found = False

    for row in csv_reader:
        row_tuple = tuple(sorted(row.items()))
        if row_tuple in seen_rows:
            duplicates_found = True
            break
        seen_rows.add(row_tuple)

    assert not duplicates_found, "Duplicate detected"


@pytest.mark.parametrize("user_id, expected_value",[
    ("1", "False"),
    ("2", "True")
])
def test_active_players(csv_reader, user_id, expected_value):
    found = False
    for row in csv_reader:
        if row['id'] == user_id:
            found = True
            assert row["is_active"] == expected_value, \
                f"Mismatch for user id {user_id}: expected is_active={expected_value}, got {row['is_active']}"
    assert found, f"User with id {user_id} was not found"


def test_active_player(csv_reader):
    found = False
    for row in csv_reader:
        if row['id'] == "2":
            found = True
            assert row["is_active"] == "True", \
                f"Expected is_active to be 'False' for id 2, got '{row['is_active']}'"
    assert found, "User with id 2 was not found"
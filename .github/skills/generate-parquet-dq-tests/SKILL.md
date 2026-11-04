---
name: generate-parquet-dq-tests
description: >-
  Creates one PyTest data-quality module per Parquet dataset from the project data mapping.
  Invoke when asked to generate or update mapped Parquet checks; refuse framework, Jenkins, or fixture changes.
disable-model-invocation: true
---

# Generate Parquet DQ tests

Complete this skill as **Step 2** of the PyTest DQ assignment. Read first:

- `PyTest DQ Framework/docs/test-automation-strategy.md` — **§5 Skill contract**, **§6 Test design standard**
- `docs/parquet-aggregated-data-mapping.md` — dataset definitions (expected SQL comes from here)

**Do not** paste expected SQL for the three named datasets into this skill.  
**Do not** instruct the agent to copy SQL from `data_dev/`.

When finished, replace every placeholder below. Run the **Skill review** checklist before using the skill to generate tests.

## When this skill applies

Use this skill only when asked to create or update dataset-level Parquet DQ tests.
Before generating a test, confirm that the framework fixtures and the methods listed in
TAS section 6.4 exist. Only edit the requested module under
`PyTest DQ Framework/tests/dq checks/parquet_files/`.

Do not use this skill to build or repair connectors, shared checks, `conftest.py`,
`pytest.ini`, dependencies, or Jenkins. If the framework is not ready, stop and report
the missing component instead of adding workarounds to a dataset test.

## Inputs you must have

Required inputs:

- Dataset folder name.
- Its output columns, transformations, grain, joins, filters, and partitioning from
  `docs/parquet-aggregated-data-mapping.md`.
- Author and requirement identifier for the module header.

If the dataset or a required transformation is missing or ambiguous in the mapping,
stop and ask for clarification. Do not fill gaps by inspecting the Parquet result or
the ETL implementation. Never use `data_dev/`, its SQL, or its loader code to create
the expected query.

## Hard rules

1. Create one file per dataset at `PyTest DQ Framework/tests/dq checks/parquet_files/test_<dataset_name>.py`.
2. PostgreSQL is expected/source data (`source_data`); Parquet is actual/target data (`target_data`).
3. Derive expected SQL only from the mapping. Do not read `data_dev/` or copy its SQL.
4. Do not add filters, `UNION`, `CASE`, sign changes, or other transformations unless the mapping says so.
5. Match the mapping's output names and grain. Use aliases for mapped output column names.
6. Read `/parquet_data/<dataset_name>` with `include_subfolders=True`.
7. Use `data_quality_library` methods for assertions; do not write pandas assertions in the test module.
8. Include smoke, completeness, count, uniqueness, and not-null checks. The not-null list is every mapped output column.
9. Mark every test `parquet_data` and with the dataset-specific marker. Add `smoke` only to the not-empty test.
10. This skill must explain a procedure, not contain concrete expected SQL for any dataset.
11. Do not add columns to expected SQL only because they appear in Parquet. Preserve and report unmapped target columns as a schema/mapping discrepancy.

## Workflow

1. Read TAS sections 5 and 6 and the requested dataset's mapping entry.
2. Write down mapped output names, grouping grain, measures, join path, filters, and partition rule.
3. Draft the PostgreSQL query from those facts only. Confirm every selected expression is either a mapped dimension or measure; alias it to the mapped name.
4. Create the module using the template below. Replace placeholders with the requested dataset's mapping details and the supplied author/requirement.
5. Add the dataset marker to all five tests; add `smoke` only to `test_check_dataset_is_not_empty`.
6. Use all mapped output columns in the not-null check. Use the mapped grain columns for the uniqueness check when the library's optional `column_names` argument is available.
7. Review the module against the checklist below. Do not rewrite expected SQL because it disagrees with Parquet.

## Template

Use this full module skeleton. Replace placeholders; do not paste dataset-specific SQL into this skill. Align source/target with TAS, not swapped names in `test_examples.py`.

```python
"""
Description: Data Quality checks for <dataset_name> dataset.
Requirement(s): <requirement_id>
Author(s): <author>
"""

import pytest


@pytest.fixture(scope='module')
def source_data(db_connection):
  source_query = """
  -- expected query derived from mapping (grain + measures + joins)
  """
  return db_connection.get_data_sql(source_query)


@pytest.fixture(scope='module')
def target_data(parquet_reader):
  target_path = '/parquet_data/<dataset_name>'
  return parquet_reader.process(target_path, include_subfolders=True)


@pytest.mark.parquet_data
@pytest.mark.smoke
@pytest.mark.<dataset_name>
def test_check_dataset_is_not_empty(target_data, data_quality_library):
  data_quality_library.check_dataset_is_not_empty(target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_data_completeness(source_data, target_data, data_quality_library):
  data_quality_library.check_data_completeness(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_count(source_data, target_data, data_quality_library):
  data_quality_library.check_count(source_data, target_data)


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_uniqueness(target_data, data_quality_library):
  data_quality_library.check_duplicates(target_data, ['<grain_col_1>', '<grain_col_2>'])


@pytest.mark.parquet_data
@pytest.mark.<dataset_name>
def test_check_not_null_values(target_data, data_quality_library):
  data_quality_library.check_not_null_values(target_data, ['<col_1>', '<col_2>', '<col_3>'])
```

## SQL derivation (generic)

Use the mapping to decide which source tables to join and which keys connect them. Put
the mapped dimensions in the grouping clause and calculate each mapped measure with
the specified aggregate and rounding. Build names using only the mapped fields and
format. Convert timestamps to dates or partition values only as specified by the
mapping. Add a filter only when the mapping explicitly lists one. Alias each result
to its mapped output name. Do not guess missing joins or transformations; ask when
the mapping does not say enough.

## After generation

Run tests only when asked. If a check fails, preserve the mapping-derived expected SQL
and report the dataset, test, mapping expectation, and observed Parquet difference.
Treat it as a possible transformation/data defect, not a reason to weaken the check.

---

## Skill review (self-check before Step 3)

The following checks passed for this skill:

- [x] Contains no concrete expected SQL for any named dataset
- [x] Forbids using `data_dev/` or Parquet loader SQL
- [x] Includes completeness, count, uniqueness, and not-null checks
- [x] Uses Postgres as source and Parquet as target; no always-pass checks
- [x] Contains no unresolved placeholders

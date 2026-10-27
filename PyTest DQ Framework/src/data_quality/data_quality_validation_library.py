import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df, column_names=None):
        duplicate_rows = df[df.duplicated(subset=column_names, keep=False)]
        columns = column_names or list(df.columns)
        assert duplicate_rows.empty, (
            f"Found {len(duplicate_rows)} duplicate rows for columns {columns}. "
            f"Sample: {duplicate_rows.head(5).to_dict(orient='records')}"
        )

    @staticmethod
    def check_count(df1, df2):
        assert len(df1) == len(df2), (
            f"Row count mismatch: expected {len(df1)}, got {len(df2)}"
        )

    @staticmethod
    def check_data_completeness(df1, df2):
        expected_columns = set(df1.columns)
        actual_columns = set(df2.columns)
        assert expected_columns == actual_columns, (
            f"Column mismatch: missing from actual={sorted(expected_columns - actual_columns)}, "
            f"unexpected in actual={sorted(actual_columns - expected_columns)}"
        )

        columns = sorted(expected_columns)
        expected_sorted = df1[columns].sort_values(
            by=columns, na_position="first"
        ).reset_index(drop=True)
        actual_sorted = df2[columns].sort_values(
            by=columns, na_position="first"
        ).reset_index(drop=True)
        pd.testing.assert_frame_equal(
            expected_sorted,
            actual_sorted,
            check_dtype=False,
            check_exact=True,
            check_like=False,
        )

    @staticmethod
    def check_dataset_is_not_empty(df):
        assert not df.empty, "Dataset is empty"

    @staticmethod
    def check_not_null_values(df, column_names=None):
        columns = column_names or list(df.columns)
        missing_columns = sorted(set(columns) - set(df.columns))
        assert not missing_columns, f"Columns not found in dataset: {missing_columns}"

        null_counts = df[columns].isna().sum()
        null_counts = null_counts[null_counts > 0].to_dict()
        assert not null_counts, f"Null values found by column: {null_counts}"

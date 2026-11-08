from datetime import datetime
from pathlib import Path

import pandas as pd
from selenium.webdriver.common.by import By


REPORT_COLUMNS = ["Facility Type", "Visit Date", "Average Time Spent"]


def _prepare_data(dataframe, filter_date):
    dataframe = dataframe[REPORT_COLUMNS].copy()
    dataframe["Facility Type"] = dataframe["Facility Type"].astype(str).str.strip()
    dataframe["Visit Date"] = pd.to_datetime(
        dataframe["Visit Date"], format="%Y-%m-%d"
    ).dt.strftime("%Y-%m-%d")
    dataframe["Average Time Spent"] = pd.to_numeric(
        dataframe["Average Time Spent"]
    )

    if filter_date:
        datetime.strptime(filter_date, "%Y-%m-%d")
        dataframe = dataframe[dataframe["Visit Date"] == filter_date]

    return dataframe.reset_index(drop=True)


def read_html_table(table_element, filter_date=None):
    """Read a located HTML table into a DataFrame."""
    table_data = {}

    for column in table_element.find_elements(By.CLASS_NAME, "y-column"):
        header = column.find_element(By.ID, "header").text.strip()
        values = []
        for cell in column.find_elements(By.CLASS_NAME, "cell-text"):
            value = cell.text.strip()
            if value and value != header:
                values.append(value)
        table_data[header] = values

    for name in REPORT_COLUMNS:
        if name not in table_data:
            raise ValueError(f"HTML table is missing column: {name}")

    return _prepare_data(pd.DataFrame(table_data), filter_date)


def read_parquet_dataset(parquet_folder, filter_date=None):
    """Read a Parquet folder and optionally filter it by visit date."""
    parquet_path = Path(parquet_folder)
    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet folder not found: {parquet_path}")

    dataframe = pd.read_parquet(parquet_path, engine="pyarrow")
    dataframe = dataframe.rename(columns={
        "facility_type": "Facility Type",
        "visit_date": "Visit Date",
        "avg_time_spent": "Average Time Spent",
    })

    return _prepare_data(dataframe, filter_date)


def compare_dataframes(html_dataframe, parquet_dataframe):
    """Compare two DataFrames and return a match result and differences."""
    if list(html_dataframe.columns) != list(parquet_dataframe.columns):
        return False, "The DataFrames have different columns."

    columns = list(html_dataframe.columns)
    html_dataframe = html_dataframe.sort_values(columns).reset_index(drop=True)
    parquet_dataframe = parquet_dataframe.sort_values(columns).reset_index(drop=True)

    if html_dataframe.equals(parquet_dataframe):
        return True, ""

    differences = []
    row_count = max(len(html_dataframe), len(parquet_dataframe))
    for row in range(row_count):
        if row >= len(html_dataframe):
            differences.append(f"Extra Parquet row: {parquet_dataframe.iloc[row].to_dict()}")
        elif row >= len(parquet_dataframe):
            differences.append(f"Missing Parquet row: {html_dataframe.iloc[row].to_dict()}")
        else:
            for column in columns:
                html_value = html_dataframe.iloc[row][column]
                parquet_value = parquet_dataframe.iloc[row][column]
                if hasattr(html_value, "item"):
                    html_value = html_value.item()
                if hasattr(parquet_value, "item"):
                    parquet_value = parquet_value.item()
                if html_value != parquet_value:
                    differences.append(
                        f"Row {row + 1}, {column}: "
                        f"HTML={html_value!r}, Parquet={parquet_value!r}"
                    )

    return False, "\n".join(differences)

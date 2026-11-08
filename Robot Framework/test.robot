*** Settings ***
Library    SeleniumLibrary
Library    ${CURDIR}${/}helper.py

*** Variables ***
${REPORT_FILE}       ${CURDIR}${/}report.html
${PARQUET_FOLDER}    ${CURDIR}${/}parquet_data${/}facility_type_avg_time_spent_per_visit_date
${FILTER_DATE}       2026-10-06

*** Test Cases ***
HTML report matches Parquet data
    [Teardown]    Close Browser
    ${report_url}=    Evaluate    pathlib.Path(r'''${REPORT_FILE}''').resolve().as_uri()    modules=pathlib
    Open Browser    ${report_url}    chrome
    Wait Until Element Is Visible    css:.table    15s
    ${table}=    Get WebElement    css:.table
    ${html_dataframe}=    Read Html Table    ${table}    ${FILTER_DATE}
    ${parquet_dataframe}=    Read Parquet Dataset    ${PARQUET_FOLDER}    ${FILTER_DATE}
    ${matches}    ${differences}=    Compare Dataframes    ${html_dataframe}    ${parquet_dataframe}
    IF    not $matches
        Fail    DataFrames differ for ${FILTER_DATE}: ${differences}
    END

import time
import os
import pandas as pd

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, \
    ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, TimeoutException


class SeleniumWebDriverContextManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        self.driver = webdriver.Chrome()
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver is not None:
            self.driver.quit()

def save_doughnut_state(driver, number):
    chart = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pielayer"))
    )
    labels = chart.find_elements(
        By.CSS_SELECTOR, "text.slicetext[data-notex='1']"
    )

    output_folder = Path(__file__).resolve().parent
    csv_path = output_folder / f"doughnut{number}.csv"
    screenshot_path = output_folder / f"screenshot{number}.png"
    columns = ["Facility Type", "Min Average Time Spent"]

    if not labels:
        pd.DataFrame(columns=columns).to_csv(csv_path, index=False)
        driver.save_screenshot(str(screenshot_path))
        print(
            f"No visible slices in state {number}. "
            f"Empty CSV and screenshot saved."
        )
        return

    rows = []
    for label in labels:
        lines = label.find_elements(By.TAG_NAME, "tspan")
        if len(lines) >= 2:
            rows.append({
                "Facility Type": lines[0].text.strip(),
                "Min Average Time Spent": lines[1].text.strip(),
            })

    pd.DataFrame(rows, columns=columns).to_csv(csv_path, index=False)
    driver.save_screenshot(str(screenshot_path))
    print(f"Doughnut saved: {csv_path} and {screenshot_path}")

if __name__ == "__main__":
    with SeleniumWebDriverContextManager() as driver:
        file_path = (
            Path(__file__).resolve().parents[2] / "generated_report" / "report.html"
        )
        driver.set_window_size(1920, 1080)
        driver.get(file_path.as_uri())
        print("Report title:", driver.title)
        try:
            table = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "table"))
            )

            columns = table.find_elements(By.CSS_SELECTOR, ".y-column")
            table_data = {}

            for column in columns:
                header = column.find_element(By.ID, "header").text.strip()
                cells = column.find_elements(By.CLASS_NAME, "cell-text")

                values = [
                    cell.text.strip()
                    for cell in cells
                    if cell.text.strip() and cell.text.strip() != header
                ]
                table_data[header] = values

            if not table_data:
                raise NoSuchElementException("No columns found in the table")

            csv_path = Path(__file__).resolve().parent / "table.csv"
            pd.DataFrame(table_data).to_csv(csv_path, index=False)
            print(f"Table saved: {csv_path}")

        except (TimeoutException, NoSuchElementException, ValueError, OSError) as error:
            print(f"Error: {error}")

        save_doughnut_state(driver, 0)

        try:
            legend = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scrollbox"))
            )
            filter_count = len(
                legend.find_elements(By.CLASS_NAME, "traces")
            )
            state_number = 1

            for filter_index in range(filter_count):
                try:
                    legend = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "scrollbox"))
                    )
                    filters = legend.find_elements(By.CLASS_NAME, "traces")
                    filters[filter_index].click()

                    time.sleep(1)
                    save_doughnut_state(driver, state_number)
                    state_number += 1

                except (
                    TimeoutException,
                    NoSuchElementException,
                    StaleElementReferenceException,
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                    IndexError,
                ) as error:
                    print(f"Could not apply filter {filter_index + 1}: {error}")

            if filter_count == 0:
                print("No chart filters were found.")

        except TimeoutException as error:
            print(f"Could not find the chart legend: {error}")
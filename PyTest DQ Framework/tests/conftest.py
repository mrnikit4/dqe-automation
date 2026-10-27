import pytest
import os

from src.connectors.postgres.postgres_connector import PostgresConnectorContextManager
from src.data_quality.data_quality_validation_library import DataQualityLibrary
from src.connectors.file_system.parquet_reader import ParquetReader


def pytest_addoption(parser):
    parser.addoption("--db_host", action="store", default="localhost", help="Database host")
    parser.addoption("--db_port", action="store", type=int, default=5434, help="Database port")
    parser.addoption("--db_name", action="store", default="mydatabase", help="Database name")
    parser.addoption("--db_user", action="store", default=os.getenv("POSTGRES_USER", ""), help="Database user")
    parser.addoption(
        "--db_password",
        action="store",
        default=os.getenv("POSTGRES_PASSWORD", ""),
        help="Database password",
    )
    parser.addoption(
        "--parquet_root",
        action="store",
        default=os.getenv("PARQUET_DATA_ROOT", "/parquet_data"),
        help="Directory containing the dataset folders",
    )


def pytest_configure(config):
    if not config.getoption("db_user"):
        pytest.fail("Missing database user: provide --db_user or POSTGRES_USER")
    if not config.getoption("db_password"):
        pytest.fail("Missing database password: provide --db_password or POSTGRES_PASSWORD")


@pytest.fixture(scope='session')
def db_connection(request):
    db_options = {
        "db_user": request.config.getoption("db_user"),
        "db_password": request.config.getoption("db_password"),
        "db_host": request.config.getoption("db_host"),
        "db_name": request.config.getoption("db_name"),
        "db_port": request.config.getoption("db_port"),
    }
    try:
        with PostgresConnectorContextManager(**db_options) as db_connector:
            yield db_connector
    except Exception as e:
        pytest.fail(f"Failed to initialize PostgresConnectorContextManager: {e}")


@pytest.fixture(scope='session')
def parquet_reader(request):
    return ParquetReader(data_root=request.config.getoption("parquet_root"))


@pytest.fixture(scope='session')
def data_quality_library():
    return DataQualityLibrary()
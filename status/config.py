from pydantic import BaseSettings


class StatusSettings(BaseSettings):
    maxtests: int = 1000
    max_results_per_category: int = 3
    report_expiration: int = 60


class SQLStorageSettings(BaseSettings):
    db_connection_url: str

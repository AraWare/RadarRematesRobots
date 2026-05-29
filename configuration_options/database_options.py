from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / "configurations.json"


@dataclass(frozen=True)
class DatabaseOptions:
    driver: str
    server: str
    database: str
    username: str
    password: str
    trust_server_certificate: str
    trusted_connection: str

    @classmethod
    def from_dict(cls, database_config: dict[str, Any]) -> "DatabaseOptions":
        driver = database_config.get("driver")
        server = database_config.get("server")
        database = database_config.get("database")
        username = database_config.get("username")
        password = database_config.get("password")
        trust_server_certificate = database_config.get("trustServerCertificate")
        trusted_connection = database_config.get("trustedConnection")

        if not isinstance(driver, str) or not driver.strip():
            raise ValueError("databaseConfigurations.driver must be a non-empty string.")

        if not isinstance(server, str) or not server.strip():
            raise ValueError("databaseConfigurations.server must be a non-empty string.")

        if not isinstance(database, str) or not database.strip():
            raise ValueError("databaseConfigurations.database must be a non-empty string.")

        if not isinstance(username, str) or not username.strip():
            raise ValueError("databaseConfigurations.username must be a non-empty string.")

        if not isinstance(password, str) or not password.strip():
            raise ValueError("databaseConfigurations.password must be a non-empty string.")

        if not isinstance(trust_server_certificate, str) or not trust_server_certificate.strip():
            raise ValueError("databaseConfigurations.trustServerCertificate must be a non-empty string.")

        if not isinstance(trusted_connection, str) or not trusted_connection.strip():
            raise ValueError("databaseConfigurations.trustedConnection must be a non-empty string.")

        return cls(
            driver=driver,
            server=server,
            database=database,
            username=username,
            password=password,
            trust_server_certificate=trust_server_certificate,
            trusted_connection=trusted_connection
        )

    @classmethod
    def from_configuration(cls) -> "DatabaseOptions":
        with CONFIG_FILE_PATH.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)

        return cls.from_dict(config.get("databaseConfigurations"))


database_options = DatabaseOptions.from_configuration()

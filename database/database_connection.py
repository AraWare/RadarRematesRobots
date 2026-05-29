import pyodbc
from configuration_options.database_options import database_options

connection = pyodbc.connect(
    f"DRIVER={database_options.driver};"
    f"SERVER={database_options.server};"
    f"DATABASE={database_options.database};"
    f"TrustServerCertificate={database_options.trust_server_certificate};"
    f"Trusted_Connection={database_options.trusted_connection};"
)


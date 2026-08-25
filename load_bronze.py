import os
import duckdb
from dotenv import load_dotenv

load_dotenv()

con = duckdb.connect("lec_stats.duckdb")

con.install_extension("httpfs")
con.load_extension("httpfs")

con.sql(f"SET s3_endpoint='{os.getenv('MINIO_ENDPOINT_HOST', 'localhost:9000')}'")
con.sql(f"SET s3_access_key_id='{os.getenv('MINIO_ROOT_USER')}'")
con.sql(f"SET s3_secret_access_key='{os.getenv('MINIO_ROOT_PASSWORD')}'")
con.sql(f"SET s3_use_ssl=false")
con.sql(f"SET s3_url_style='path'")

con.sql("""
    CREATE OR REPLACE TABLE matches_raw AS
    SELECT * FROM read_json_auto('s3://bronze/lec/summer2026/*.json')
""")

con.sql("SELECT COUNT(*) FROM matches_raw").show()

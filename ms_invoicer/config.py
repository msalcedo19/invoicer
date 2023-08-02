import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

# Database
URL_CONNECTION = os.environ.get(
    "URL_CONNECTION", "postgresql://postgres:postgres@localhost/invoicer"
)

# S3
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "invoicer-dev-01")

# PDF
WKHTMLTOPDF_PATH = os.environ.get("WKHTMLTOPDF_PATH", "/usr/local/bin/wkhtmltopdf")

# Security
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ.get("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

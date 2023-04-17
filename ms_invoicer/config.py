import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

# Database
URL_CONNECTION = os.environ.get("URL_CONNECTION", "postgresql://postgres:postgres@localhost/invoicer")

# s3
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY", "")

#PDF
WKHTMLTOPDF_PATH = os.environ.get("WKHTMLTOPDF_PATH", "/usr/local/bin/wkhtmltopdf")

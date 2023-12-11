from config import settings

LOG_LEVEL = settings.LOG_LEVEL

# Database
URL_CONNECTION = settings.URL_CONNECTION

# S3
S3_ACCESS_KEY = settings.S3_ACCESS_KEY
S3_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY
S3_BUCKET_NAME = settings.S3_BUCKET_NAME

# PDF
WKHTMLTOPDF_PATH = settings.WKHTMLTOPDF_PATH

# Security
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

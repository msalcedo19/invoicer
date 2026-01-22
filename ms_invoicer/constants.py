from enum import Enum


class LogEvent(str, Enum):
    REQUEST_TIMING = "request_timing"
    CREATE_FOLDER = "create_folder"
    REMOVE_FILE = "remove_file"
    UPLOAD_FILE = "upload_file"
    DOWNLOAD_FILE = "download_file"
    DELETE_FILE = "delete_file"
    ENSURE_DATABASE_EXISTS = "ensure_database_exists"
    INIT_DB = "init_db"
    CREATE_INVOICE_FROM_FILE = "create_invoice_from_file"

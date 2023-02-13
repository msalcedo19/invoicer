import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

#Database
URL_CONNECTION = os.environ.get("URL_CONNECTION", "mysql://msalcedo:password@localhost/invoicer")
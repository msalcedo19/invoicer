from datetime import datetime, timedelta, time
import os
import logging

log = logging.getLogger(__name__)

def check_dates(base_date: datetime, date1: time, date2: time = None) -> datetime:
    """
    """
    result = datetime.combine(base_date, date1)
    if date2 and date1 < date2:
        result = result + timedelta(days=1)
    return result


def create_folders():
    folder_name = "temp"
    if not os.path.exists(folder_name):
        log.info("Creating folder {} ...".format(folder_name))
        os.mkdir(folder_name)
    else:
        log.info("Folder does exist")

    folder_name = "temp/xlsx"
    if not os.path.exists(folder_name):
        log.info("Creating folder {} ...".format(folder_name))
        os.mkdir(folder_name)
    else:
        log.info("Folder does exist")

    folder_name = "temp/pdf"
    if not os.path.exists(folder_name):
        log.info("Creating folder {} ...".format(folder_name))
        os.mkdir(folder_name)
    else:
        log.info("Folder does exist")


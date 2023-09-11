from typing import Union
import logging
import os
import boto3

from typing import List
from fastapi import UploadFile
from datetime import datetime, time, timedelta
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell

from ms_invoicer.config import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY

log = logging.getLogger(__name__)


def check_dates(base_date: datetime, date1: time, date2: time = None) -> datetime:
    """ """
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


def save_file(file_path: str, file: UploadFile):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "wb") as output_file:
        output_file.write(file.file.read())


def remove_file(file_path: str):
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print(f"'{file_path}' not found!")


def find_ranges(sheet: Worksheet) -> List[tuple]:
    """
    This function takes an Excel worksheet (using the openpyxl library) as input,
    searches for a specific string in the first column of the sheet, and returns
    a list of tuples representing the row ranges that contain the string.

    Input:

    sheet: an Excel worksheet object (type: Worksheet)

    Output:

    A list of tuples, where each tuple contains four integers representing the
    starting and ending rows of a range that contains the target string.

    Functionality:

    The function iterates through each row of the given worksheet, stopping at
    row 200 and column 10. For each row, it checks the value of the first cell
    (column A). If the value is a non-empty string containing the text "NOM CONTRAT",
    the function records the starting row number and adds a tuple to the result list.
    The tuple contains the starting row number, the row number 2 rows below the
    starting row, the row number 4 rows below the starting row, and the row number
    34 rows below the starting row. These row numbers are calculated based on the
    assumption that each contract occupies 31 rows (31 days in a month).
    """
    result = []
    start_num = None
    end_num = None
    for row in sheet.iter_rows(max_col=10, max_row=200):
        row_data: Cell = row[0]
        if (
            row_data.value
            and isinstance(row_data.value, str)
            and row_data.value.startswith("NOM CONTRAT")
        ):
            start_num = int(row_data.row)
        elif (
            row_data.value
            and isinstance(row_data.value, str)
            and row_data.value.startswith("TOTAL")
        ):
            end_num = int(row_data.row)

        if start_num and end_num:
            result.append((start_num, start_num + 2, start_num + 4, end_num))
            start_num = None
            end_num = None
    return result


def upload_file(
    file_path: str,
    file_name: str,
    bucket="invoicer-dev-01",
    object_name=None,
    is_pdf=False,
):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Upload the file
    session: boto3.Session = boto3.session.Session()
    s3 = session.client(
        "s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    )
    try:
        args = {"ACL": "public-read"}
        if is_pdf:
            try:
                download_filename = file_name.split("-")[0]
            except:
                download_filename = file_name
            args = {
                "ACL": "public-read",
                "ContentType": "application/pdf",
                "ContentDisposition": 'inline; filename="{}.pdf"'.format(
                    download_filename
                ),
            }
        s3.upload_file(
            file_path,
            bucket,
            object_name,
            ExtraArgs=args,
        )
        url = "https://" + bucket + ".s3.amazonaws.com/" + file_name
        return url
    except Exception as e:
        log.error(e)
        raise Exception("Failure uploading file")


def delete_file_from_s3(file_names: Union[str, list], bucket_name="invoicer-dev-01"):
    try:
        # Create a session using your AWS credentials
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        )
        if isinstance(file_names, list):
            for file_name in file_names:
                s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        else:
            s3_client.delete_object(Bucket=bucket_name, Key=file_names)
    except Exception as e:
        log.error(e)
        raise Exception("Failure deleting file")

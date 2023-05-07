import logging
from math import ceil
import os
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

import boto3
import openpyxl
from botocore.exceptions import ClientError
from fastapi import UploadFile
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from ms_invoicer.config import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY
from ms_invoicer.dao import FilesToProcessData, FilesToProcessEvent, PdfToProcessEvent
from ms_invoicer.db_pool import get_db
from ms_invoicer.event_bus import publish
from ms_invoicer.sql_app import crud, schemas

log = logging.getLogger(__name__)


def save_file(file_path: str, file: UploadFile):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "wb") as output_file:
        output_file.write(file.file.read())


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
            # result.append((start_num, start_num + 2, start_num + 4, start_num + 34))
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


async def process_file(
    file: UploadFile,
    invoice_id: int,
    bill_to_id: int,
    current_user_id: int,
    col_letter: str = "F",
) -> schemas.File:
    try:
        date_now = datetime.now()
        filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.xlsx"
        file_path = "temp/xlsx/{}".format(filename)
        save_file(file_path, file)

        price_unit = 1
        currency = "CAD"
        s3_url = upload_file(file_path=file_path, file_name=filename)
        file_obj = schemas.FileCreate(
            **{
                "s3_xlsx_url": s3_url,
                "s3_pdf_url": None,
                "created": datetime.now(),
                "invoice_id": invoice_id,
                "bill_to_id": bill_to_id,
                "user_id": current_user_id,
            }
        )
        new_file = crud.create_file(db=next(get_db()), model=file_obj)
        data_event = FilesToProcessData(
            file_path=file_path,
            file_id=new_file.id,
            invoice_id=invoice_id,
            current_user_id=current_user_id,
            price_unit=price_unit,
            col_letter=col_letter,
            currency=currency,
        )
        await publish(FilesToProcessEvent(data=data_event))
        return new_file
    except Exception as e:
        log.error("File processing failed")
        log.error(e)
        raise


async def extract_data(event: FilesToProcessEvent) -> bool:
    event_handled = False
    conn = next(get_db())
    try:
        col_letter = event.data.col_letter
        currency = event.data.currency

        xlsx_file = Path(event.data.xlsx_url)
        wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)
        for sheet_name in wb_obj.sheetnames:
            sheet: Cell = wb_obj[sheet_name]

            ranges = find_ranges(sheet)
            for range_of in ranges:
                (minrowinfo, maxrowinfo, minrow, maxrow) = range_of
                contract_dict = {}
                for row in sheet.iter_rows(
                    min_row=minrowinfo, max_row=maxrowinfo, max_col=10
                ):
                    cell = row[0].value
                    if cell:
                        if "NOM CONTRAT" in cell:
                            contract_dict["title"] = row[2].value
                        elif "HEURE" in cell:
                            contract_dict["price_unit"] = row[2].value
                        elif "MONTANT" in cell:
                            contract_dict["total_amount"] = row[2].value
                hours = 0
                for col in range(minrow, maxrow):
                    hour = sheet["{}{}".format(col_letter, col)].value
                    hours += float(round(hour, 2))

                price_unit = contract_dict.get("price_unit", None)
                amount = 0
                if not price_unit:
                    amount = int(contract_dict.get("total_amount", 1))
                    price_unit = round(amount / hours, 2)
                else:
                    amount = hours * float(price_unit)

                contract_dict["hours"] = hours
                contract_dict["currency"] = currency
                contract_dict["amount"] = amount
                contract_dict["price_unit"] = price_unit
                contract_dict["file_id"] = event.data.file_id
                contract_dict["invoice_id"] = event.data.invoice_id
                contract_dict["user_id"] = event.data.current_user_id
                service_created = schemas.ServiceCreate(**contract_dict)
                crud.create_service(db=conn, model=service_created)

        invoice_obj: schemas.Invoice = crud.get_invoice(
            db=conn,
            model_id=event.data.invoice_id,
            current_user_id=event.data.current_user_id,
        )
        file_obj: schemas.File = crud.get_file(
            db=conn,
            model_id=event.data.file_id,
            current_user_id=event.data.current_user_id,
        )
        data_event = PdfToProcessEvent(
            current_user_id=event.data.current_user_id,
            invoice=invoice_obj,
            file=file_obj,
            html_template_name="template01.html",
            xlsx_url=event.data.xlsx_url,
        )
        await publish(data_event)
        event_handled = True
        return event_handled
    except Exception as e:
        log.error("Extracting data failed")
        log.error(e)
        raise


def upload_file(
    file_path: str, file_name: str, bucket="invoicer-files-dev", object_name=None
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
        s3.upload_file(file_path, bucket, object_name, ExtraArgs={"ACL": "public-read"})
        url = "https://" + bucket + ".s3.amazonaws.com/" + file_name
        return url
    except ClientError as e:
        logging.error(e)
    return None

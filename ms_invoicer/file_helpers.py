from datetime import datetime
from math import floor
from typing import List
import openpyxl
from fastapi import UploadFile
from pathlib import Path
import logging
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.utils import check_dates
from ms_invoicer.dao import FilesToProcessData, FilesToProcessEvent, PdfToProcessEvent
from ms_invoicer.event_bus import publish
from ms_invoicer.db_pool import get_db
from ms_invoicer.config import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY
import boto3
from botocore.exceptions import ClientError
import os
from uuid import uuid4
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell

log = logging.getLogger(__name__)


def save_file(file_path: str, file: UploadFile):
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "wb") as output_file:
        output_file.write(file.file.read())


def find_ranges(sheet: Worksheet) -> List[tuple]:
    result = []
    for row in sheet.iter_rows(max_col=10, max_row=200):
        row_data: Cell = row[0]
        if (
            row_data.value
            and isinstance(row_data.value, str)
            and "NOM CONTRAT" in row_data.value
        ):
            start_num = int(row_data.row)
            result.append((start_num, start_num + 3, start_num + 5, start_num + 35))
    return result

async def process_file(
    file_path: str, invoice_id: int, col_letter: str = "G"
) -> schemas.File:
    try:
        xlsx_file = Path(file_path)
        wb_obj = openpyxl.load_workbook(xlsx_file)

        for sheet_name in wb_obj.sheetnames:
            sheet = wb_obj[sheet_name]

            ranges = find_ranges(sheet)
            for range in ranges:
                (_, _, minrow, maxrow) = range
                index = minrow
                for row in sheet.iter_rows(min_row=minrow, max_row=maxrow):
                    (row_date, in_time, start_break_time, end_break_time, out_time) = (
                        row[0],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                    )
                    date_1 = check_dates(row_date.value, in_time.value)
                    date_2 = check_dates(
                        row_date.value, start_break_time.value, in_time.value
                    )
                    date_3 = check_dates(
                        row_date.value, end_break_time.value, in_time.value
                    )
                    date_4 = check_dates(row_date.value, out_time.value, in_time.value)
                    amount = (date_4 - date_3) + (date_3 - date_2) + (date_2 - date_1)
                    sheet["{}{}".format(col_letter, index)] = floor(
                        amount.seconds / 3600
                    )
                    log.debug(
                        "date1: {} - date2: {} - date3: {} - date4: {} - result: {}".format(
                            date_1,
                            date_2,
                            date_3,
                            date_4,
                            sheet["G{}".format(index)].value,
                        )
                    )
                    index += 1

                sheet[
                    "{}{}".format(col_letter, maxrow + 1)
                ] = "=SUM({}{}:{}{})".format(col_letter, minrow, col_letter, maxrow)
                middlerow = minrow + 14
                sheet[
                    "{}{}".format(col_letter, maxrow + 2)
                ] = "=SUM({}{}:{}{})".format(col_letter, minrow, col_letter, middlerow)
                sheet[
                    "{}{}".format(col_letter, maxrow + 3)
                ] = "=SUM({}{}:{}{})".format(
                    col_letter, middlerow + 1, col_letter, maxrow
                )

        date_now = datetime.now()
        filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.xlsx"
        file_path = "temp/{}".format(filename)
        wb_obj.save(file_path)

        price_unit = 1
        currency = "CAD"
        s3_url = upload_file(file_path=file_path, file_name=filename)
        file_obj = schemas.FileCreate(
            **{
                "s3_xlsx_url": s3_url,
                "s3_pdf_url": None,
                "created": datetime.now(),
                "invoice_id": invoice_id,
            }
        )
        new_file = crud.create_file(db=next(get_db()), model=file_obj)
        data_event = FilesToProcessData(
            files_to_process=[file_path],
            file_id=new_file.id,
            invoice_id=invoice_id,
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
    try:
        col_letter = event.data.col_letter
        currency = event.data.currency

        conn = next(get_db())
        invoice_obj: schemas.Invoice = crud.get_invoice(
            db=conn, model_id=event.data.invoice_id
        )
        file_obj: schemas.File = crud.get_file(db=conn, model_id=event.data.file_id)
        contract_obj = crud.get_contract(db=conn, model_id=invoice_obj.contract_id)
        price_unit = contract_obj.price_unit
        for file in event.data.files_to_process:
            xlsx_file = Path(file)
            wb_obj = openpyxl.load_workbook(xlsx_file)
            for sheet_name in wb_obj.sheetnames:
                sheet = wb_obj[sheet_name]

                ranges = find_ranges(sheet)
                for range_of in ranges:
                    (minrowinfo, maxrowinfo, minrow, maxrow) = range_of
                    contract_dict = {}
                    for row in sheet.iter_rows(min_row=minrowinfo, max_row=maxrowinfo, max_col=10):
                        cell = row[0].value
                        if cell:
                            if "NOM CONTRAT" in cell:
                                contract_dict["title"] = row[2].value
                            elif "PÉRIODE" in cell:
                                contract_dict["period"] = row[2].value
                    hours = 0
                    for col in range(minrow, maxrow):
                        hours += int(sheet["{}{}".format(col_letter, col)].value)
                    contract_dict["hours"] = hours
                    contract_dict["currency"] = currency
                    contract_dict["amount"] = contract_dict["hours"] * price_unit
                    contract_dict["price_unit"] = price_unit
                    contract_dict["file_id"] = event.data.file_id
                    service_created = schemas.ServiceCreate(**contract_dict)
                    crud.create_service(db=next(get_db()), model=service_created)

        
        data_event = PdfToProcessEvent(
            invoice=invoice_obj,
            file=file_obj,
            html_template_name="template01.html",
            contract=contract_obj
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

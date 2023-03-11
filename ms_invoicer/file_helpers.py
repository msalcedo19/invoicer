from datetime import datetime
from math import floor
import openpyxl
from fastapi import UploadFile
from pathlib import Path
import logging
from ms_invoicer.sql_app import crud, schemas, models
from ms_invoicer.utils import check_dates
from ms_invoicer.file_dao import FilesToProcessData, FilesToProcessEvent
from ms_invoicer.event_bus import publish
from ms_invoicer.db_pool import get_db

log = logging.getLogger(__name__)


def save_file(file_path: str, file: UploadFile):
    with open(file_path, "wb") as output_file:
        output_file.write(file.file.read())


async def process_file(
    file_path: str, output_path: str, invoice_id: int, col_letter: str = "G"
) -> schemas.FileCreate:
    try:
        xlsx_file = Path(file_path)
        wb_obj = openpyxl.load_workbook(xlsx_file)
        sheet = wb_obj.active

        output_file = Path(output_path)
        output_wb_obj = openpyxl.load_workbook(output_file)
        output_sheet = output_wb_obj.active
        index = 7
        for row in sheet.iter_rows(min_row=7, max_row=37):
            (row_date, in_time, start_break_time, end_break_time, out_time) = (
                row[0],
                row[2],
                row[3],
                row[4],
                row[5],
            )
            date_1 = check_dates(row_date.value, in_time.value)
            date_2 = check_dates(row_date.value, start_break_time.value, in_time.value)
            date_3 = check_dates(row_date.value, end_break_time.value, in_time.value)
            date_4 = check_dates(row_date.value, out_time.value, in_time.value)
            amount = (date_4 - date_3) + (date_3 - date_2) + (date_2 - date_1)
            output_sheet["{}{}".format(col_letter, index)] = floor(
                amount.seconds / 3600
            )
            log.debug(
                "date1: {} - date2: {} - date3: {} - date4: {} - result: {}".format(
                    date_1,
                    date_2,
                    date_3,
                    date_4,
                    output_sheet["H{}".format(index)].value,
                )
            )
            index += 1

        output_sheet["{}38".format(col_letter)] = "=SUM({}7:{}37)".format(
            col_letter, col_letter
        )
        output_sheet["{}39".format(col_letter)] = "=SUM({}7:{}21)".format(
            col_letter, col_letter
        )
        output_sheet["{}40".format(col_letter)] = "=SUM({}22:{}37)".format(
            col_letter, col_letter
        )

        output_wb_obj.save(output_path)
        price_unit = 1
        currency = "CAD"
        data_event = FilesToProcessData(files_to_process=[output_path], invoice_id=invoice_id, price_unit=price_unit, col_letter=col_letter, currency=currency)
        await publish(FilesToProcessEvent(data=data_event))
        return schemas.FileCreate(
            **{
                "s3_xlsx_url": output_path,
                "s3_pdf_url": None,
                "created": datetime.now(),
                "invoice_id": invoice_id,
            }
        )
    except Exception as e:
        log.error("File processing failed")
        log.error(e)
        raise


def extract_data(
    event: FilesToProcessEvent
) -> bool:
    event_handled = False
    try:
        col_letter = event.data.col_letter
        currency = event.data.currency
        price_unit = event.data.price_unit
        invoice_services = []
        for file in event.data.files_to_process:
            xlsx_file = Path(file)
            wb_obj = openpyxl.load_workbook(xlsx_file)
            sheet = wb_obj.active

            contract_dict = {}
            for row in sheet.iter_rows(min_row=2, max_row=4):
                for i in range(0, len(row)):
                    cell = row[i].value
                    if cell:
                        if "NOM CONTRAT" in cell:
                            contract_dict["title"] = row[i + 2].value
                        elif "PÉRIODE" in cell:
                            contract_dict["period"] = row[i + 2].value
            hours = 0
            for col in range(7, 38):
                hours += int(sheet["{}{}".format(col_letter, col)].value)
            contract_dict["hours"] = hours
            contract_dict["currency"] = currency
            contract_dict["amount"] = contract_dict["hours"] * price_unit
            contract_dict["price_unit"] = price_unit
            contract_dict["invoice_id"] = event.data.invoice_id
            service_created = schemas.ServiceCreate(**contract_dict)
            new_service = crud.create_service(db=next(get_db()), model=service_created)
            invoice_services.append(new_service)

        event_handled = True
        return event_handled
    except Exception as e:
        log.error("Extracting data failed")
        log.error(e)
        raise

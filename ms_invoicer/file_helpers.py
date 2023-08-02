import logging
import openpyxl

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from openpyxl.cell.cell import Cell
from ms_invoicer.config import S3_BUCKET_NAME

from ms_invoicer.dao import FilesToProcessData, FilesToProcessEvent, PdfToProcessEvent
from ms_invoicer.db_pool import get_db
from ms_invoicer.event_bus import publish
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.utils import save_file, find_ranges, upload_file

log = logging.getLogger(__name__)


async def process_file(
    file: UploadFile,
    invoice_id: int,
    bill_to_id: int,
    current_user_id: int,
    col_letter: str = "F",
    with_taxes: bool = True
) -> schemas.File:
    try:
        log.info("Customer {} - Processing file".format(current_user_id)) #TODO: Mejorar mensaje en los logs (Hay mensajes que se repiten y no se puede saber donde fallo)
        date_now = datetime.now()
        filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.xlsx"
        filename = filename.replace(" ", "_")
        file_path = "temp/xlsx/{}".format(filename)
        save_file(file_path, file)
        log.info("Customer {} - File saved".format(current_user_id))

        price_unit = 1
        currency = "CAD"
        log.info("Customer {} - Uploading file".format(current_user_id))
        s3_url = upload_file(file_path=file_path, file_name=filename, bucket=S3_BUCKET_NAME)
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
            with_taxes=with_taxes
        )
        log.info("Customer {} - Publishing process event".format(current_user_id))
        await publish(FilesToProcessEvent(data=data_event))
        return new_file
    except Exception as e:
        log.error(e)
        log.error("Customer {} - Failure processing file".format(current_user_id))
        raise


async def extract_data(event: FilesToProcessEvent) -> bool:
    log.info("Customer {} - Extracting data".format(event.data.current_user_id))
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
            invoice_update = False
            for range_of in ranges:
                (minrowinfo, maxrowinfo, minrow, maxrow) = range_of
                if not invoice_update:
                    crud.patch_invoice(
                        db=conn,
                        model_id=event.data.invoice_id,
                        current_user_id=event.data.current_user_id,
                        update_dict={
                            "created": sheet["{}{}".format("A", maxrow - 1)].value
                        },
                    )
                    invoice_update = True
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
        template: schemas.Template = crud.get_template(
            db=conn, current_user_id=event.data.current_user_id
        )
        template_name = "template01.html"
        if not event.data.with_taxes:
            template_name = "template03.html"
        elif template:
            template_name = template.name

        data_event = PdfToProcessEvent(
            current_user_id=event.data.current_user_id,
            invoice=invoice_obj,
            file=file_obj,
            html_template_name=template_name,
            xlsx_url=event.data.xlsx_url,
            with_taxes=event.data.with_taxes
        )
        log.info("Customer {} - Publishing pdf event".format(event.data.current_user_id))
        await publish(data_event)
        event_handled = True
        return event_handled
    except Exception as e:
        log.error("Customer {} - Failure extracting data".format(event.data.current_user_id))
        log.error(e)
        raise

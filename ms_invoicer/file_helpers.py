from ctypes import Union
import logging
import shutil
import os
from re import I
from typing import Dict, List, Tuple, Union
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session
from openpyxl.cell.cell import Cell
from ms_invoicer.config import S3_BUCKET_NAME

from ms_invoicer.dao import FilesToProcessEvent, PdfToProcessEvent
from ms_invoicer.db_pool import get_db
from ms_invoicer.event_bus import publish
from ms_invoicer.sql_app import crud, schemas
from ms_invoicer.sql_app import models
from ms_invoicer.sql_app.models import Invoice, User
from ms_invoicer.utils import download_file_from_s3, extract_and_get_month_name, remove_file, save_file, find_ranges, upload_file

log = logging.getLogger(__name__)


def extract_pages(file: Union[UploadFile, None], current_user_id: int) -> List[str]:
    log.info("Customer {} - Getting pages - fun: get_pages".format(current_user_id))
    date_now = datetime.now()
    filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.xlsx"
    filename = filename.replace(" ", "_")
    file_path = "temp/xlsx/{}".format(filename)
    save_file(file_path, file)
    xlsx_file = Path(file_path)
    wb_obj = openpyxl.load_workbook(xlsx_file)
    results = wb_obj.sheetnames
    remove_file(file_path)
    return results


async def process_file(
    file: Union[UploadFile, None],
    invoice_id: int,
    bill_to_id: int,
    current_user_id: int,
    col_letter: str = "F",
    pages: List[str] = [],
) -> schemas.File:
    if file is None:
        return None, None
    try:
        log.info(
            "Customer {} - Processing file - fun: process_file".format(current_user_id)
        )
        date_now = datetime.now()
        filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.xlsx"
        filename = filename.replace(" ", "_")
        file_path = "temp/xlsx/{}".format(filename)
        save_file(file_path, file)
        log.info("Customer {} - File saved - fun: process_file".format(current_user_id))

        price_unit = 1
        currency = "CAD"
        log.info(
            "Customer {} - Uploading file - fun: process_file".format(current_user_id)
        )
        s3_url = upload_file(
            file_path=file_path, file_name=filename, bucket=S3_BUCKET_NAME
        )
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
        data_event = FilesToProcessEvent(
            file_path=file_path,
            file_id=new_file.id,
            invoice_id=invoice_id,
            current_user_id=current_user_id,
            price_unit=price_unit,
            col_letter=col_letter,
            currency=currency,
            pages=pages,
        )
        log.info(
            "Customer {} - Publishing process event - fun: process_file".format(
                current_user_id
            )
        )
        await publish(data_event)
        return new_file, file_path
    except Exception as e:
        log.error(
            "Customer {} - Failure processing file - fun: process_file - err: {}".format(
                current_user_id, e
            )
        )
        raise


async def extract_data(event: FilesToProcessEvent) -> bool:
    log.info(
        "Customer {} - Extracting data - fun: extract_data".format(
            event.current_user_id
        )
    )
    event_handled = False
    conn = next(get_db())
    try:
        col_letter = event.col_letter
        currency = event.currency

        xlsx_file = Path(event.xlsx_url)
        wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)
        for sheet_name in wb_obj.sheetnames:
            if sheet_name not in event.pages:
                continue
            sheet: Cell = wb_obj[sheet_name]

            ranges = find_ranges(sheet)
            invoice_update = False
            for range_of in ranges:
                (minrowinfo, maxrowinfo, minrow, maxrow) = range_of
                if not invoice_update:
                    crud.patch_invoice(
                        db=conn,
                        model_id=event.invoice_id,
                        current_user_id=event.current_user_id,
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
                contract_dict["file_id"] = event.file_id
                contract_dict["invoice_id"] = event.invoice_id
                contract_dict["user_id"] = event.current_user_id
                service_created = schemas.ServiceCreate(**contract_dict)
                crud.create_service(db=conn, model=service_created)

        invoice_obj: schemas.Invoice = crud.get_invoice(
            db=conn,
            model_id=event.invoice_id,
            current_user_id=event.current_user_id,
        )
        file_obj: schemas.File = crud.get_file(
            db=conn,
            model_id=event.file_id,
            current_user_id=event.current_user_id,
        )
        template: schemas.Template = crud.get_template(
            db=conn, current_user_id=event.current_user_id
        )
        template_name = "template01.html"
        if not invoice_obj.with_taxes:
            template_name = "template03.html"
        elif template:
            template_name = template.name

        data_event = PdfToProcessEvent(
            current_user_id=event.current_user_id,
            invoice=invoice_obj,
            file=file_obj,
            html_template_name=template_name,
            xlsx_url=event.xlsx_url,
        )
        log.info(
            "Customer {} - Publishing pdf event - fun: extract_data".format(
                event.current_user_id
            )
        )
        # await publish(data_event)
        event_handled = True
        return event_handled
    except Exception as e:
        log.error(
            "Customer {} - Failure extracting data - fun: extract_data - err: {}".format(
                event.current_user_id, e
            )
        )
        raise


async def process_pdf(
    db: Session,
    invoice: Invoice,
    bill_to_id: int,
    contracts: List[schemas.ServiceCreateNoFile],
    current_user: User,
    new_file_obj: schemas.File,
    xlsx_local_path: str,
):
    log.info(
        "Customer {} - Processing file without file - fun: process_pdf".format(
            current_user.id
        )
    )  # TODO: Modificar mensajes
    with_file = False
    if not new_file_obj:
        file_obj = schemas.FileCreate(
            **{
                "s3_xlsx_url": None,
                "s3_pdf_url": None,
                "created": datetime.now(),
                "invoice_id": invoice.id,
                "bill_to_id": bill_to_id,
                "user_id": current_user.id,
            }
        )
        new_file = crud.create_file(db=db, model=file_obj)
    else:
        new_file = new_file_obj
        with_file = True
    log.info("Customer {} - File created - fun: process_pdf".format(current_user.id))

    result = []
    for contract in contracts:
        obj_dict = contract.dict()
        obj_dict["user_id"] = current_user.id
        obj_dict["invoice_id"] = invoice.id
        obj_dict["file_id"] = new_file.id
        result.append(
            crud.create_service(db=db, model=schemas.ServiceCreate(**obj_dict))
        )
    log.info(
        "Customer {} - Contracts created - fun: process_pdf".format(current_user.id)
    )

    template_name = "template01.html"
    if not invoice.with_taxes:
        template_name = "template03.html"
    data_event = PdfToProcessEvent(
        current_user_id=current_user.id,
        invoice=invoice,
        file=new_file,
        html_template_name=template_name,
        xlsx_url=xlsx_local_path,
        with_file=with_file,
    )
    log.info(
        "Customer {} - Publishing pdf event - fun: process_pdf".format(current_user.id)
    )
    await publish(data_event)
    return crud.get_file(db=db, model_id=new_file.id, current_user_id=current_user.id)


async def generate_summary_by_date(
    db: Session,
    customer_id: int,
    current_user: User,
    start_date: datetime,
    end_date: datetime,
):
    invoices_by_customer = crud.get_invoices_by_customer_and_date_range(
        db=db,
        model_id=customer_id,
        current_user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )

    xlsx_list: List[models.File] = []
    for invoice in invoices_by_customer:
        files_list = crud.get_files_by_invoice(db=db, model_id=invoice.id, current_user_id=current_user.id)
        xlsx_list.extend(files_list)

    xlsx_path_name_list: List[str] = []
    for xlsx in xlsx_list:
        filename = f"to_process_{xlsx.invoice_id}_{xlsx.id}_{xlsx.user_id}.xlsx"
        file_path = "temp/xlsx/{}".format(filename)
        xlsx_path_name_list.append(file_path)
        if not os.path.exists(file_path) and xlsx.s3_xlsx_url is not None:
            splitted_name = xlsx.s3_xlsx_url.split("/")
            download_file_from_s3(file_path_s3=splitted_name[3], path_to_save=file_path, bucket=S3_BUCKET_NAME)
        
    
    try:
        customer_obj = crud.get_customer(db=db, model_id=customer_id, current_user_id=current_user.id)
        output_filename = "resumen_{}_{}_{}-{}_{}.xlsx".format(customer_obj.name.replace(" ", "_"), start_date.month, start_date.year, end_date.month, end_date.year)
        output_file_path = "temp/xlsx/{}".format(output_filename)
        shutil.copy("scripts/summary_template.xlsx", output_file_path)
        new_workbook = openpyxl.load_workbook(output_file_path)
        pair_sheet_names: Dict[str, List[Tuple]] = {}
        for path in xlsx_path_name_list:
            xlsx_file = Path(path)
            wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)

            if path not in pair_sheet_names:
                pair_sheet_names[path] = []

            for _, sheet_name in enumerate(wb_obj.sheetnames):
                sheet: Worksheet = wb_obj[sheet_name]
                new_sheet: Worksheet = new_workbook["01"]
                new_worksheet: Worksheet  = new_workbook.copy_worksheet(new_sheet)
                pair_sheet_names[path].append((sheet.title, new_worksheet.title))

        index_contract = 1
        for path in xlsx_path_name_list:
            xlsx_file = Path(path)
            wb_obj = openpyxl.load_workbook(xlsx_file, data_only=True)
            for (input_sheet_name, output_sheet_name) in pair_sheet_names[path]:
                input_sheet: Worksheet = wb_obj[input_sheet_name]

                new_sheet_wb: Worksheet = new_workbook[output_sheet_name]
                new_sheet_wb.title = "Contrat {}".format(index_contract)
                index_contract += 1

                ranges = find_ranges(input_sheet)
                period_extracted = False
                for range_of in ranges:
                    (minrowinfo, maxrowinfo, minrow, maxrow) = range_of
                    for row in input_sheet.iter_rows(
                        min_row=minrowinfo, max_row=maxrowinfo, max_col=10
                    ):
                        cell = row[0].value
                        if cell:
                            if "NOM CONTRAT" in cell:
                                cell_new_wb = new_sheet_wb["C1"]
                                cell_new_wb.value = row[2].value

                    if not period_extracted:
                        new_sheet_wb["{}{}".format("C", 2)].value = extract_and_get_month_name(input_sheet["{}{}".format("A", minrow)].value)
                        period_extracted = True
                    
                    # Values
                    for col in range(minrow, maxrow):
                        input_date_value = input_sheet["{}{}".format("A", col)].value
                        new_sheet_wb["{}{}".format("A", col)].value = input_date_value

                        input_date_value = input_sheet["{}{}".format("B", col)].value
                        new_sheet_wb["{}{}".format("C", col)].value = input_date_value

                        input_date_value = input_sheet["{}{}".format("C", col)].value
                        new_sheet_wb["{}{}".format("D", col)].value = input_date_value

                        input_date_value = input_sheet["{}{}".format("D", col)].value
                        new_sheet_wb["{}{}".format("E", col)].value = input_date_value

                        input_date_value = input_sheet["{}{}".format("E", col)].value
                        new_sheet_wb["{}{}".format("F", col)].value = input_date_value

                        input_date_value = input_sheet["{}{}".format("F", col)].value
                        new_sheet_wb["{}{}".format("G", col)].value = input_date_value

                    if maxrow - minrow <= 30:
                        new_sheet_wb.delete_rows(36)
                        new_sheet_wb["{}{}".format("G", 36)].value = "=SUM(G6:G35)"
                        new_sheet_wb["{}{}".format("G", 38)].value = "=SUM(G22:G35)"
                        new_sheet_wb["{}{}".format("I", 36)].value = "=SUM(I6:I35)"
                        new_sheet_wb["{}{}".format("K", 36)].value = "=SUM(K6:K35)"
                        
        original_sheet = new_workbook["01"]
        new_workbook.remove(original_sheet)
        new_workbook.save(output_file_path)
        # Close the workbook
        new_workbook.close()
        s3_url = upload_file(
            file_path=output_file_path, file_name=output_filename, bucket=S3_BUCKET_NAME
        )
        return s3_url

    except Exception as e:
        log.error(
            "Customer {} - Failure generating summary - fun: generate_summary_by_date - err: {}".format(
                current_user.id, e
            )
        )
        raise
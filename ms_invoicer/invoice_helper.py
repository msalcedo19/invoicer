from datetime import datetime
from bs4 import BeautifulSoup
import os
import bs4
import jinja2
import pdfkit
from ms_invoicer.file_helpers import upload_file
from ms_invoicer.dao import PdfToProcessEvent
from ms_invoicer.sql_app import crud
from ms_invoicer.db_pool import get_db

from uuid import uuid4

base = os.path.dirname(os.path.dirname(__file__))


def build_pdf(event: PdfToProcessEvent):
    assert event.html_template_name.endswith(".html")
    assert event.file.bill_to is not None
    assert len(event.file.services) != 0

    connection = next(get_db())
    input_html_path: str = os.path.join(
        base, "templates/base/{}".format(event.html_template_name)
    )
    output_html_path: str = os.path.join(
        base, "templates/{}".format(event.html_template_name)
    )
    with open(input_html_path) as fp:
        soup = BeautifulSoup(fp, "html.parser")

        new_tag = soup.new_tag("div")
        for index in range(0, len(event.file.services)):
            new_tr_tag = soup.new_tag("tr")
            for variable in [
                "service_id",
                "service_txt",
                "num_hours",
                "amount",
            ]:
                new_td_tag = soup.new_tag("td")
                new_td_tag.string = "{{" + variable + str(index) + "}}"
                new_tr_tag.append(new_td_tag)
            new_tag.append(new_tr_tag)
        for comment in soup.find_all(string=lambda e: isinstance(e, bs4.Comment)):
            if "items" in comment:
                comment.replace_with(new_tag)

        with open(output_html_path, "w") as file:
            file.write(str(soup))

        top_info_data = {}
        top_info = crud.get_topinfos(db=connection)
        if len(top_info) > 0:
            top_info = top_info[0]
            top_info_data["top_info_from"] = top_info.ti_from
            top_info_data["top_info_addr"] = top_info.addr
            top_info_data["top_info_phone"] = top_info.phone
            top_info_data["top_info_email"] = top_info.email

        bill_to_data = {}
        if event.file.bill_to:
            bill_to_data["to"] = event.file.bill_to.to
            bill_to_data["addr"] = event.file.bill_to.addr
            bill_to_data["phone"] = event.file.bill_to.phone
            bill_to_data["email"] = event.file.bill_to.email

        service_data = {}
        subtotal = 0
        index = 0
        for service in event.file.services:
            service_data["service_id{}".format(index)] = index+1
            service_data["service_txt{}".format(index)] = service.title
            service_data["num_hours{}".format(index)] = service.hours
            #service_data["per_hour{}".format(index)] = service.price_unit
            service_data["amount{}".format(index)] = service.amount
            subtotal += service.amount
            index += 1

        total_tax_1 = (event.invoice.tax_1/100) * subtotal
        total_tax_2 = (event.invoice.tax_2/100) * subtotal
        total = total_tax_1 + total_tax_2 + subtotal
        context = {
            "invoice_id": event.invoice.number_id,
            "created": event.invoice.created,
            "total_no_taxes": round(subtotal, 2),
            "total_tax1": round(total_tax_1, 2),
            "total_tax2": round(total_tax_2, 2),
            "total": round(total, 2),
        }
        context |= bill_to_data
        context |= service_data
        context |= top_info_data

        template_loader = jinja2.FileSystemLoader(os.path.join(base, "templates"))
        template_env = jinja2.Environment(loader=template_loader)

        template = template_env.get_template(event.html_template_name)
        output_text = template.render(context)

        date_now = datetime.now()
        filename = f"{date_now.year}{date_now.month}{date_now.day}{date_now.hour}{date_now.minute}{date_now.second}-{str(uuid4())}.pdf"
        output_pdf_path: str = "temp/pdf/{}".format(filename)
        config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf") #TODO: Modificar en la máquina
        pdfkit.from_string(output_text, output_pdf_path, configuration=config)

        s3_pdf_url = upload_file(file_path=output_pdf_path, file_name=filename)
        crud.patch_file(
            db=connection,
            model_id=event.file.id,
            update_dict={"s3_pdf_url": s3_pdf_url},
        )
        return True

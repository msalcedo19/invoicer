from datetime import datetime
from bs4 import BeautifulSoup
import os
import bs4
import jinja2
import pdfkit
from ms_invoicer.sql_app import crud, schemas, models

base = os.path.dirname(os.path.dirname(__file__))


def build_pdf(
    html_name: str,
    pdf_name: str,
    invoice: schemas.Invoice
):
    assert html_name.endswith(".html")
    assert pdf_name.endswith(".pdf")
    assert invoice.bill_to is not None
    assert len(invoice.services) != 0

    input_html_path: str = os.path.join(base, "templates/base/{}".format(html_name))
    output_html_path: str = os.path.join(base, "templates/{}".format(html_name))
    with open(input_html_path) as fp:
        soup = BeautifulSoup(fp, "html.parser")

        new_tag = soup.new_tag("div")
        for index in range(0, len(invoice.services)):
            new_tr_tag = soup.new_tag("tr")
            for variable in [
                "service_id",
                "service_txt",
                "num_hours",
                "per_hour",
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

        bill_to_data = {}
        if invoice.bill_to:
            bill_to_data["to"] = invoice.bill_to.to
            bill_to_data["addr"] = invoice.bill_to.addr
            bill_to_data["phone"] = invoice.bill_to.phone

        service_data = {}
        for service in invoice.services:
            service_data["service_id"] = service.id
            service_data["service_txt"] = service.title
            service_data["num_hours"] = service.hours
            service_data["per_hour"] = service.price_unit
            service_data["amount"] = service.amount

        total_tax_1 = invoice.tax_1 * invoice.subtotal
        total_tax_2 = invoice.tax_2 * invoice.subtotal
        total = total_tax_1 + total_tax_2 + invoice.subtotal
        context = {
            "invoice_id": invoice.id,
            "created": invoice.created,
            "total_no_taxes": invoice.subtotal,
            "total_tax1": total_tax_1 ,
            "total_tax2": total_tax_2,
            "total": total
        }
        context |= bill_to_data
        context |= service_data

        template_loader = jinja2.FileSystemLoader(os.path.join(base, "templates"))
        template_env = jinja2.Environment(loader=template_loader)

        template = template_env.get_template(html_name)
        output_text = template.render(context)
        
        output_pdf_path: str = os.path.join(base, "temp/pdf/{}".format(pdf_name))
        config = pdfkit.configuration(wkhtmltopdf="/usr/local/bin/wkhtmltopdf")
        pdfkit.from_string(output_text, output_pdf_path, configuration=config)


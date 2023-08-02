from ms_invoicer.event_bus import Event
from ms_invoicer.sql_app.schemas import File, Invoice


class FilesToProcessData:
    xlsx_url: str
    price_unit: int
    col_letter: str
    currency: str
    file_id: int
    invoice_id: int
    current_user_id: int
    with_taxes: int

    def __init__(
        self,
        file_path: str,
        file_id: int,
        invoice_id: int,
        current_user_id: int,
        price_unit: int,
        col_letter: str,
        currency: str,
        with_taxes: bool,
    ) -> None:
        self.xlsx_url = file_path
        self.file_id = file_id
        self.invoice_id = invoice_id
        self.current_user_id = current_user_id
        self.price_unit = price_unit
        self.col_letter = col_letter
        self.currency = currency
        self.with_taxes = with_taxes


class FilesToProcessEvent(Event): #TODO: Remove this class
    """
    TODO: Add description
    """

    def __init__(self, data: FilesToProcessData):
        self.data = data


class PdfToProcessEvent(Event):
    """
    TODO: Add description
    """

    def __init__(
        self,
        current_user_id: int,
        invoice: Invoice,
        file: File,
        html_template_name: str,
        xlsx_url: str,
        with_file: bool = True,
        with_taxes = True,
    ):
        self.current_user_id = current_user_id
        self.invoice = invoice
        self.file = file
        self.html_template_name = html_template_name
        self.xlsx_url = xlsx_url
        self.with_file = with_file
        self.with_taxes = with_taxes


class GenerateFinalPDF(Event):
    """
    TODO: Add description
    """

    def __init__(
        self,
        current_user_id: int,
        pdf_tables: str,
        xlsx_url: str,
        pdf_invoice: str,
        filename: str,
        file_id: int,
    ):
        self.current_user_id = current_user_id
        self.path_pdf_tables = pdf_tables
        self.xlsx_url = xlsx_url
        self.path_pdf_invoice = pdf_invoice
        self.filename = filename
        self.file_id = file_id

class GenerateFinalPDFNoFile(Event):
    """
    TODO: Add description
    """

    def __init__(
        self,
        current_user_id: int,
        pdf_invoice: str,
        filename: str,
        file_id: int,
    ):
        self.current_user_id = current_user_id
        self.path_pdf_invoice = pdf_invoice
        self.filename = filename
        self.file_id = file_id

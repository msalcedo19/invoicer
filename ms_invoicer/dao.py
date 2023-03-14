from ms_invoicer.event_bus import Event
from typing import Any, Dict, List

from ms_invoicer.sql_app.schemas import Invoice, File

class FilesToProcessData():
    files_to_process: List[Dict[str, Any]]
    price_unit: int
    col_letter: str
    currency: str
    file_id: int
    invoice_id: int

    def __init__(self, files_to_process: List[Dict[str, Any]], file_id: int, invoice_id: int, price_unit: int, col_letter: str, currency: str) -> None:
        self.files_to_process = files_to_process
        self.file_id = file_id
        self.invoice_id = invoice_id
        self.price_unit = price_unit
        self.col_letter = col_letter
        self.currency = currency


class FilesToProcessEvent(Event):
    """
    TODO: Add description
    """

    def __init__(self, data: FilesToProcessData):
        self.data = data


class PdfToProcessEvent(Event):
    """
    TODO: Add description
    """
    def __init__(self, invoice: Invoice, file: File, html_template_name: str):
        self.invoice = invoice
        self.file = file
        self.html_template_name = html_template_name

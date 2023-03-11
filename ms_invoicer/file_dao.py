from ms_invoicer.event_bus import Event
from typing import Any, Dict, List

class FilesToProcessData():
    files_to_process: List[Dict[str, Any]]
    price_unit: int
    col_letter: str
    currency: str
    invoice_id: int

    def __init__(self, files_to_process: List[Dict[str, Any]], invoice_id: int, price_unit: int, col_letter: str, currency: str) -> None:
        self.files_to_process = files_to_process
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


class InvoiceToProcessEvent(Event):
    """
    TODO: Add description
    """

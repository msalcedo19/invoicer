from ms_invoicer.dao import FilesToProcessEvent, GenerateFinalPDFNoFile, GenerateFinalPDFWithFile, PdfToProcessEvent
from ms_invoicer.event_bus import register
from ms_invoicer.file_helpers import extract_data
from ms_invoicer.invoice_helper import build_pdf, generate_invoice, generate_invoice_no_file


def register_event_handlers():
    """
    Entry-point for registering all event handlers with the event bus.
    """
    register(FilesToProcessEvent, extract_data)
    register(PdfToProcessEvent, build_pdf)
    register(GenerateFinalPDFWithFile, generate_invoice)
    register(GenerateFinalPDFNoFile, generate_invoice_no_file)

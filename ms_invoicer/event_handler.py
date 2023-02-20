from ms_invoicer.event_bus import register
from ms_invoicer.file_helpers import extract_data
from ms_invoicer.file_dao import FilesToProcessEvent


def register_event_handlers():
    """
    Entry-point for registering all event handlers with the event bus.
    """
    register(FilesToProcessEvent, extract_data)
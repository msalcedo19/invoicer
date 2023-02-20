from ms_invoicer.event_bus import Event
from typing import Any, Dict, List

class FilesToProcessEvent(Event):
    """
    TODO: Add description
    """

    def __init__(self, files_to_process: List[Dict[str, Any]]):
        self.files_to_process = files_to_process
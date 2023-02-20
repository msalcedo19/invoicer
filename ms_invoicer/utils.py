from datetime import datetime, timedelta, time

def check_dates(base_date: datetime, date1: time, date2: time = None) -> datetime:
    """
    """
    result = datetime.combine(base_date, date1)
    if date2 and date1 < date2:
        result = result + timedelta(days=1)
    return result

from datetime import timezone
import datetime, pytz

def get_dates_between_timestamps(start_timestamp_ms, end_timestamp_ms):
    start_timestamp_s = start_timestamp_ms / 1000
    end_timestamp_s = end_timestamp_ms / 1000
    
    utc = pytz.UTC
    start_date = datetime.datetime.fromtimestamp(start_timestamp_s, utc)
    end_date = datetime.datetime.fromtimestamp(end_timestamp_s, utc)
    
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    date_range = []
    current_date = start_date
    
    while current_date <= end_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    return date_range


def convert_date_to_unix_timestamp(date_input):
    if isinstance(date_input, str):
        date_input = datetime.datetime.strptime(date_input, "%Y-%m-%d")
    date_input = date_input.replace(hour=0, minute=0, second=0, microsecond=0)
    date_input = date_input.replace(tzinfo=timezone.utc)
    unix_timestamp_ms = int(date_input.timestamp() * 1000)
    return unix_timestamp_ms

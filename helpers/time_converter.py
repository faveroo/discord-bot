import re

def parse_time(time_str: str) -> int:
    """
    Converte '2h30m', '10s', '1d' em segundos.
    """
    pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.fullmatch(pattern, time_str)

    if not match:
        return None
    
    days, hours, minutes, seconds = match.groups(default="0")
    total_seconds = (
        int(days) * 86400 +
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds)
    )

    return total_seconds if total_seconds > 0 else None
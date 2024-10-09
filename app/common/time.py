from datetime import datetime, timezone, timedelta


def utc_now_offset(days=0,
                   hours=0,
                   minutes=0,
                   seconds=0,
                   milliseconds=0,
                   microseconds=0):
    return datetime.now(timezone.utc) + timedelta(days=days,
                                                  hours=hours,
                                                  minutes=minutes,
                                                  seconds=seconds,
                                                  milliseconds=milliseconds,
                                                  microseconds=microseconds)

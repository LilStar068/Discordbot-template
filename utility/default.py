import time


def timestamp(thing, ago: bool = False, mode: str = "f"):
    output = int(time.mktime(thing.timetuple()))
    timestamp = f"<t:{output}:{mode}>"
    if ago:
        timestamp += f" (<t:{output}:R>)"
    return timestamp
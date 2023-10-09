from collections import OrderedDict


INTERVALS = OrderedDict([
    ('h', 3600),
    ('m', 60),
    ('s', 1)
])


def human_time(seconds, decimals=1):
    '''Human-readable time from seconds (ie. 1h 25m).
    Examples:
        >>> human_time(15)
        '15s'
        >>> human_time(3600)
        '1h'
        >>> human_time(3720)
        '1h 2m'
        >>> human_time(266400)
        '74h'
        >>> human_time(-1.5)
        '-1.5s'
        >>> human_time(0)
        '0s'
        >>> human_time(0.1)
        '100ms'
        >>> human_time(1)
        '1s'
        >>> human_time(1.234, 2)
        '1.23s'
    Args:
        seconds (int or float): Duration in seconds.
        decimals (int): Number of decimals.
    Returns:
        str: Human-readable time.
    Comes from:
        github.com/leonardlan
    '''
    if seconds < 0:
        if isinstance(seconds, int):
            ret = str(round(seconds, decimals)) + ' s'
        else:
            ret = str(seconds) + ' s'
        return ret
    elif seconds == 0:
        return '0 sec'
    elif 0 < seconds < 1:
        # Return in milliseconds.
        ms = int(seconds * 1000)
        return '%i ms' % (ms)
    elif 1 < seconds < INTERVALS['m']:
        if isinstance(seconds, int):
            ret = str(seconds) + ' s'
        else:
            ret = str(round(seconds, decimals)) + ' s'
        return ret

    res = []
    for interval, count in INTERVALS.items():
        quotient, remainder = divmod(seconds, count)
        if quotient >= 1:
            seconds = remainder
            res.append('%i%s' % (int(quotient), interval))
        if remainder == 0:
            break

    if len(res) >= 1:
        # Only shows 2 most important intervals.
        return '{} {}'.format(res[0], res[1])
    return res[0]

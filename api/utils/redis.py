# -*- coding: utf8 -*-

import json
import redis

from distutils.util import strtobool
from loguru import logger

from variables import REDIS_BASE, REDIS_HOST, REDIS_PORT

try:
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_BASE)
except Exception as e:
    logger.error(f'Redis Connection KO (r) [{e}]')
else:
    logger.debug('Redis Connection OK (r)')


def str2typed(string: str):
    """
    Convert a string to its appropriate Python data type.

    This function checks if the string represents None, a boolean, or an integer,
    and returns the corresponding typed value. If none of these apply, it returns
    the string as-is.

    Parameters:
    string (str): The input string to be converted.

    Returns:
    The appropriately typed value: None, bool, int, or str.
    """
    # Normalize the input by stripping whitespace and converting to lowercase
    # Check if the string matches any known representations of None
    if string.strip().lower() in ("none", "null", "nil", ""):
        return None

    # Check if the string can be interpreted as a boolean
    try:
        return bool(strtobool(string))
    except ValueError:
        pass

    # Check if the string is an integer
    try:
        return int(string)
    except ValueError:
        pass
    else:
        return string

    # Check if the string is a valid JSON object
    try:
        return json.loads(string)
    except (json.JSONDecodeError, TypeError):
        pass

    # Otherwise, return the string itself
    return string

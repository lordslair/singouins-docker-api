# -*- coding: utf8 -*-

import re

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax


def str2typed(string):
    # BOOLEAN False
    if string == 'False':
        return False
    # BOOLEAN True
    elif string == 'True':
        return True
    # None
    elif string == 'None':
        return None
    # INT (just in case an INT gets in the mix)
    elif isinstance(string, int):
        return string
    # Date
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', string):
        return string
    # INT
    elif string.isdigit():
        return int(string)
    else:
        return string


def typed2str(string):
    # None
    if string is None:
        return 'None'
    # BOOLEAN True
    elif string is True:
        return 'True'
    # BOOLEAN False
    elif string is False:
        return 'False'
    else:
        return string

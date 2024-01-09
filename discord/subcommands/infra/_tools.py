# -*- coding: utf8 -*-

import re


def log_pretty(log):
    # We do this to filter out ANSI sequences (ex: colors)
    reaesc = re.compile(r'\x1b[^m]*m')
    exec_stdout_purged = reaesc.sub('', log)

    # We do this to have the latest lines, not the first
    exec_stdout_pretty = []
    content_length = 0  # to count the final message length
    for line in exec_stdout_purged.splitlines():
        if content_length + len(line) < 2000:
            if 'WARN' in line.upper():
                newline = f'🟧 {line}\n'
            elif 'ERROR' in line.upper():
                newline = f'🟥 {line}\n'
            elif 'INFO' in line.upper():
                newline = f'🟩 {line}\n'
            elif 'DEBUG' in line.upper():
                newline = f'🟦 {line}\n'
            elif 'TRACE' in line.upper():
                newline = f'🟦 {line}\n'
            else:
                newline = f'⬜ {line}\n'

            content_length += len(newline)
            exec_stdout_pretty.append(newline)
        else:
            break

    return exec_stdout_pretty

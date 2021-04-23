# -*- coding: utf8 -*-

from .fn_user           import fn_user_get_from_discord

#
# Queries /admin/user/*
#

# API: POST /admin/user
def admin_user(discordname):

    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)

    user = fn_user_get_from_discord(discordname)
    if user:
        return (200,
                True,
                f'Discordname found (discordname:{discordname})',
                user)
    else:
        return (200,
                False,
                f'Discordname not found (discordname:{discordname})',
                None)

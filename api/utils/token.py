# -*- coding: utf8 -*-

from itsdangerous import URLSafeTimedSerializer

from variables    import SEP_SECRET_KEY, SEP_SECRET_KEY as SEP_SECRET_SALT


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SEP_SECRET_KEY)
    return serializer.dumps(email, salt=SEP_SECRET_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SEP_SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SEP_SECRET_SALT,
            max_age=expiration
        )
    except Exception:
        return False
    return email

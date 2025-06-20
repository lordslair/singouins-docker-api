# -*- coding: utf8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger

from variables import env_vars


def send(adress, subject, body):
    message = MIMEMultipart()
    message['From'] = env_vars['SMTP_FROM']
    message['To'] = adress
    message['Subject'] = subject

    message_content = MIMEText(body, "html")
    message.attach(message_content)

    try:
        mail = smtplib.SMTP_SSL(env_vars['SMTP_SERVER'], local_hostname=env_vars['SMTP_HOSTNAME'])
        mail.connect(host=env_vars['SMTP_SERVER'])
        mail.ehlo()
        mail.set_debuglevel(0)
        mail.login(env_vars['SMTP_USER'], env_vars['SMTP_PASS'])
        mail.sendmail(message["From"], message["To"], message.as_string())
        mail.close()
    except smtplib.SMTPException as e:
        logger.error(f'Sending EMail KO [{e}]')
        return False
    else:
        logger.trace('Sending EMail OK')
        return True

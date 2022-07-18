# -*- coding: utf8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from loguru               import logger

from utils.variables import SMTP_FROM, SMTP_SERVER, SMTP_USER, SMTP_PASS, SMTP_HOSTNAME

def send(adress, subject, body):

    message            = MIMEMultipart()
    message['From']    = SMTP_FROM
    message['To']      = adress
    message['Subject'] = subject

    message_content = MIMEText(body,"html")
    message.attach(message_content)

    try:
        mail = smtplib.SMTP_SSL(SMTP_SERVER,
                                local_hostname = SMTP_HOSTNAME)
        mail.ehlo()
        mail.set_debuglevel(0)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.sendmail(message["From"],message["To"],message.as_string())
        mail.close()
    except smtplib.SMTPException as e:
        logger.error(f'Sending EMail KO [{e}]')
        return False
    else:
        logger.trace(f'Sending EMail OK')
        return True

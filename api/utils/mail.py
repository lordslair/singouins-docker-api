# -*- coding: utf8 -*-

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText

from utils.variables import SMTP_FROM, SMTP_SERVER, SMTP_USER, SMTP_PASS, SMTP_HOSTNAME

def send(adress, subject, body):

    message            = MIMEMultipart()
    message['From']    = SMTP_FROM
    message['To']      = adress
    message['Subject'] = subject

    message_content = MIMEText(body,"plain")
    message.attach(message_content)

    try:
        mail = smtplib.SMTP_SSL(SMTP_SERVER,
                                local_hostname = SMTP_HOSTNAME)
        mail.ehlo()
        mail.set_debuglevel(0)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.sendmail(message["From"],message["To"],message.as_string())
        mail.close()
        return True
    except smtplib.SMTPException as e:
        print(e)
        return False

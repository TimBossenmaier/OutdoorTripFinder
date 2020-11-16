import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app


def send_email(to, subject, template, **kwargs):

    msg = MIMEMultipart('alternative')
    msg["Subject"] = current_app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject
    msg["From"] = current_app.config['MAIL_SENDER']
    msg["To"] = to

    body = open('app/templates/' + template + '.txt', 'r').read().format(**kwargs)
    html = open('app/templates/' + template + '.html', 'r').read().format(**kwargs)

    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    ssl_context = ssl.create_default_context()
    with smtplib.SMTP_SSL(current_app.config['MAIL_SERVER'],
                          current_app.config['MAIL_PORT'],
                          context=ssl_context) as server:
        server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        server.sendmail(current_app.config['MAIL_SENDER'], to, msg.as_string())

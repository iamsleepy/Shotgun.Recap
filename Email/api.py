import smtplib
import os
from email.mime.text import MIMEText


def SendEmail(address='', body=''):
    smtp_server = os.getenv('EMAIL_SERVER')
    if smtp_server is None:
        print("Error: Missing address and EMAIL_SERVER in system environment. Can't send email.")
        return
    # The default smtp server port is 587
    server = smtplib.SMTP(smtp_server, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    user = os.getenv('EMAIL_USER')
    passwd = os.getenv('EMAIL_PASSWORD')
    if address == '':
        address = os.getenv('EMAIL_RECEIVER')
        if address is None:
            print("Error: Missing address and EMAIL_RECEIVER in system environment. Can't send email.")
            server.quit()
            return

    if user is None or passwd is None:
        print("Error: Missing EMAIL_USER or EMAIL_PASSWORD in system environment. Can't send email.")
        server.quit()
        return
    server.login(user, passwd)
    msg = MIMEText(body)
    msg['Subject'] = 'Notification'
    msg['From'] = user
    msg['To'] = address
    server.sendmail(user, address, msg.as_string())
    server.quit()

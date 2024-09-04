import config as cfg
import DataStore as ds
import smtplib, ssl
import socket
import logging
import socket
import threading


logger = logging.getLogger(__name__)

def mailit(text: str):
    """
    The `mailit` function sends an email with a specified subject and text using the SMTP protocol.
    
    :param subject: The subject of the email that you want to send
    :type subject: str
    :param text: The `text` parameter is a string that represents the body of the email message. It can
    contain any text or HTML content that you want to include in the email
    :type text: str
    """
    try:
        subject = f"message from: {ds.DS.ds['System']['ProgName']['CURRENT_DATA']} running on: {ds.DS.ds['System']['MyName']['CURRENT_DATA']}"
    except:
        subject = ("message from: unknown System")
    
    if cfg.ini['Mailing']:
        threading.Thread(target=_mailit_thread, args=(subject, text), daemon=True).start()

def _mailit_thread(subject, text):
    to = 'follrichs@icloud.com'
    mail_user = 'follrichs@gmx.de'
    mail_pwd = 'kHh%aHvC%H4RK8pf5q4S'
    context = ssl.create_default_context()
    smtpserver = smtplib.SMTP("mail.gmx.net",587)
    smtpserver.ehlo()
    smtpserver.starttls(context=context)
    smtpserver.ehlo()
    smtpserver.login(mail_user, mail_pwd)
    header = f"To:{to}\nFrom: {mail_user}\nSubject: {subject}\n"
    msg = f"{header}{text}\r\n     ------------------------------------------------------------     \r\n     ------------    below follows GMX waste    ------------     \r\n     ------------------------------------------------------------     \r\n"
    logger.info(f"Mailing to: {to}; Subject: {subject}; content: {text}")
    smtpserver.sendmail(mail_user, to.split(","), msg)
    smtpserver.close()

if __name__ == "__main__":
    _mailit_thread("qwertz", "text")
#    mailit("this is the message")

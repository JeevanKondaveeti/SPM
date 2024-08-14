import smtplib
'''SMTP - simple mail transfer protocol '''
from smtplib import SMTP
from email.message import EmailMessage

def semdmail(to,body,subject):
    server = smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('kondaveetijeevan@gmail.com',"rxco ytvu wpwo srbm")
    msg= EmailMessage()
    msg['FROM'] = 'kondaveetijeevan@gmail.com'
    msg['TO'] = to
    msg.set_content(body)
    msg['SUBJECT'] = subject
    server.send_message(msg)
    server.close()
    print(f"otp sent {to}")
    
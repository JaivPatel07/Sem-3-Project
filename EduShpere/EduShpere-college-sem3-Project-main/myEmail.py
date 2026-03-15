import smtplib
from email.message import EmailMessage
import numpy
import math

class SendEmail:
    def result_email(reciver,user_name,course_title,score):
        sender_email = ""
        sender_password = ""
        receiver_email = reciver

        msg = EmailMessage()
        msg["Subject"] = f"Student Performance Report – [{course_title}]"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(f"Hello! '{user_name[0]}' \n you had successfully completed '{course_title}' course \non EduSphere with {math.trunc(score)}% \ndownload your certificate from EduSphere")

        # Connect to Gmail SMTP server
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        except Exception as e:
            print('error to send mail:- ',e)

    def admin_login_email(user):
        otp = numpy.random.randint(1001,9999)
        sender_email = ""
        sender_password = ""
        receiver_email = ''

        msg = EmailMessage()
        msg["Subject"] = f"Admin Login Otp"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(f"Hello! {user} Verify Your Otp:- {otp}")

        # Connect to Gmail SMTP server
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print('email send success fully')
        except Exception as e:
            print('error to send mail:- ',e)
        return otp
        

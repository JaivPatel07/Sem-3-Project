import logging
import math
import os
import secrets
import smtplib
from email.message import EmailMessage


class SendEmail:
    logger = logging.getLogger(__name__)

    @classmethod
    def _smtp_settings(cls):
        sender_email = os.getenv('SMTP_SENDER_EMAIL')
        sender_password = os.getenv('SMTP_SENDER_PASSWORD')
        if not sender_email or not sender_password:
            cls.logger.warning('SMTP credentials are not configured. Email delivery is disabled.')
            return None

        return {
            'sender_email': sender_email,
            'sender_password': sender_password,
            'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '465')),
        }

    @classmethod
    def _send_email(cls, receiver_email, subject, body):
        settings = cls._smtp_settings()
        if not settings or not receiver_email:
            return False

        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = settings['sender_email']
        message['To'] = receiver_email
        message.set_content(body)

        try:
            with smtplib.SMTP_SSL(settings['host'], settings['port']) as server:
                server.login(settings['sender_email'], settings['sender_password'])
                server.send_message(message)
            return True
        except Exception:
            cls.logger.exception('Failed to send email')
            return False

    @classmethod
    def result_email(cls, receiver, user_name, course_title, score):
        body = (
            f"Hello {user_name},\n\n"
            f"You successfully completed '{course_title}' on EduSphere with {math.trunc(score)}%.\n"
            'You can now download your certificate from EduSphere.'
        )
        return cls._send_email(receiver, f"Student Performance Report - [{course_title}]", body)

    @classmethod
    def admin_login_email(cls, user, receiver_email):
        otp = secrets.randbelow(900000) + 100000
        body = f'Hello {user},\n\nUse this OTP to finish your EduSphere institute login: {otp}'
        if not cls._send_email(receiver_email, 'EduSphere Login OTP', body):
            return None
        return otp
        

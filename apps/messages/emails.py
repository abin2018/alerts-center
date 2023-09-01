from .base import MessageSendingBase
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import os


class EmailMessageSending(MessageSendingBase):
    def send(self) -> dict:
        # 第三方 SMTP 服务
        mail_host = os.environ.get("MAIL_HOST")
        mail_user = os.environ.get("MAIL_USER")
        mail_pass = os.environ.get("MAIL_PASS")
        sender = mail_user
        subject = self.message_body["subject"]
        message = self.message_body["message"]
        message_obj = MIMEText(message, 'plain', 'utf-8')  # 邮件内容
        message_obj['Subject'] = Header(subject, 'utf-8')
        smtp_obj = smtplib.SMTP_SSL(mail_host)
        smtp_obj.connect(mail_host, 465)
        smtp_obj.login(mail_user, mail_pass)
        return smtp_obj.sendmail(sender, self.target, message_obj.as_string())

    def process_on_call(self, on_call_stuff_object) -> None:
        email_address = on_call_stuff_object.stuff_email
        self.target = email_address

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib


class MailMaster:
    def __init__(self):
        self.server = smtplib.SMTP('smtp.163.com', 25)
        self.server.set_debuglevel(1)
        self.from_addr = 'tryking_monitor@163.com'
        self.password = 'monitor1234'

    def send_mail(self, header='default_header', message='default_msg', to_addrs=['tryking@foxmail.com'], file_path=None):
        msg = MIMEMultipart()
        msg['From'] = 'Migu Search Crawler'
        # msg['To'] = self._format_addr('管理员 <%s>' % to_addr)
        msg['To'] = ','.join(to_addrs)
        msg['Subject'] = Header(header)
        message = MIMEText(message)
        msg.attach(message)

        if file_path is not None:
            # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
            with open(file_path, 'rb') as f:
                # 设置附件的MIME和文件名，这里是png类型:
                mime = MIMEApplication(f.read())
                # 加上必要的头信息:
                mime.add_header('Content-Disposition', 'attachment', filename=self.get_file_name(file_path))
                msg.attach(mime)

        self.server.login(self.from_addr, self.password)
        self.server.sendmail(self.from_addr, to_addrs, msg.as_string())
        self.server.quit()

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8'), addr))

    @staticmethod
    def get_file_name(file_path):
        try:
            file_part = os.path.split(file_path)
            return file_part[len(file_part) - 1]
        except Exception as e:
            pass


if __name__ == '__main__':
    mail = MailMaster()
    print(mail.get_file_name('output\dsfds.excel'))

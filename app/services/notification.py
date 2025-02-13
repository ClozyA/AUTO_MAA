#   <AUTO_MAA:A MAA Multi Account Management and Automation Tool>
#   Copyright © <2024> <DLmaster361>

#   This file is part of AUTO_MAA.

#   AUTO_MAA is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published
#   by the Free Software Foundation, either version 3 of the License,
#   or (at your option) any later version.

#   AUTO_MAA is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
#   the GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with AUTO_MAA. If not, see <https://www.gnu.org/licenses/>.

#   DLmaster_361@163.com

"""
AUTO_MAA
AUTO_MAA通知服务
v4.2
作者：DLmaster_361
"""
import requests
from loguru import logger
from plyer import notification
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from serverchan_sdk import sc_send

from app.core import Config


class Notification:

    def push_notification(self, title, message, ticker, t):
        """推送系统通知"""

        if Config.global_config.get(Config.global_config.notify_IfPushPlyer):

            notification.notify(
                title=title,
                message=message,
                app_name="AUTO_MAA",
                app_icon=str(Config.app_path / "resources/icons/AUTO_MAA.ico"),
                timeout=t,
                ticker=ticker,
                toast=True,
            )

        return True

    def send_mail(self, title, content):
        """使用官方专用邮箱推送邮件通知"""

        # 声明：此邮箱为AUTO_MAA项目组资产，未经授权不得私自使用
        # 注意：此声明注释只有使用者更换发信邮箱时才能删除，本条规则优先级高于GPLv3

        if Config.global_config.get(Config.global_config.notify_IfSendMail):

            # 第三方 SMTP 服务配置
            mail_host = "smtp.163.com"  # 设置服务器
            mail_sender = "AUTO_MAA_server@163.com"  # 用户名
            mail_key = "SYrq87nDLD4RNB5T"  # 授权码 24/11/15

            # 定义邮件正文
            message = MIMEText(content, "plain", "utf-8")
            message["From"] = formataddr(
                (
                    Header("AUTO_MAA通知服务", "utf-8").encode(),
                    "AUTO_MAA_server@163.com",
                )
            )  # 发件人显示的名字
            message["To"] = formataddr(
                (
                    Header("AUTO_MAA用户", "utf-8").encode(),
                    Config.global_config.get(Config.global_config.notify_MailAddress),
                )
            )  # 收件人显示的名字
            message["Subject"] = Header(title, "utf-8")

            try:
                smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 465为SMTP_SSL默认端口
                smtpObj.login(mail_sender, mail_key)
                smtpObj.sendmail(
                    mail_sender,
                    Config.global_config.get(Config.global_config.notify_MailAddress),
                    message.as_string(),
                )
                return True
            except smtplib.SMTPException as e:
                return f"发送邮件时出错：\n{e}"
            finally:
                smtpObj.quit()

    def ServerChanPush(self, title, content):
        """使用Server酱推送通知"""

        if Config.global_config.get(Config.global_config.notify_IfServerChan):
            send_key = Config.global_config.get(Config.global_config.notify_ServerChanKey)
            option = {}
            is_valid = lambda s: s == "" or (s == '|'.join(s.split('|')) and (s.count('|') == 0 or all(s.split('|'))))
            """
            is_valid => True, 如果启用的话需要正确设置Tag和Channel。
            允许空的Tag和Channel即不启用，但不允许例如a||b，|a|b，a|b|，||||
            """
            send_tag = Config.global_config.get(Config.global_config.notify_ServerChanTag)
            send_channel = Config.global_config.get(Config.global_config.notify_ServerChanChannel)

            if is_valid(send_tag):
                option['tags'] = send_tag
            else:
                option['tags'] = ''
                logger.warning('请正确设置Auto_MAA中ServerChan的Tag。')

            if is_valid(send_channel):
                option['channel'] = send_channel
            else:
                option['channel'] = ''
                logger.warning('请正确设置Auto_MAA中ServerChan的Channel。')

            response = sc_send(send_key, title, content, option)
            if response["code"] == 0:
                logger.info("Server酱推送通知成功")
                return True
            else:
                logger.info("Server酱推送通知失败")
                logger.error(response)
                return f'使用Server酱推送通知时出错：\n{response["data"]['error']}'

    def CompanyWebHookBotPush(self, title, content):
        """使用企业微信群机器人推送通知"""
        if Config.global_config.get(Config.global_config.notify_IfCompanyWebHookBot):
            content = f'{title}\n{content}'
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            response = requests.post(
                url=Config.global_config.get(Config.global_config.notify_CompanyWebHookBotUrl),
                json=data
            )
            if response.json()["errcode"] == 0:
                logger.info("企业微信群机器人推送通知成功")
                return True
            else:
                logger.info("企业微信群机器人推送通知失败")
                logger.error(response.json())
                return f'使用企业微信群机器人推送通知时出错：\n{response.json()["errmsg"]}'


Notify = Notification()

from pathlib import Path
from typing import Any

import yagmail
from loguru import logger as log


def send_mail(
    receivers: str | list[str],
    subject: str,
    message: Any,
    smtp_sender: str,
    smtp_password: str,
    smtp_server: str,
    smtp_port: int = 465,
    smtp_tls: bool = True,
    attachments: list[str | Path] | None = None,
) -> None:
    """Send smtp mail.

    Args:
        receivers: receivers which the mail should be sent to.
            either a mail address, or a list of mail addresses.
        subject: subject of the mail.
        message: mail body.
        smtp_sender: sender mail address.
        smtp_password: password of the mail sender.
        smtp_server: smtp server to connect to.
        smtp_port: smtp port to connect to.
        smtp_tls: if TLS/SSL should be used. False means StartTLS will be used.
        attachments: any file attachments to add.

    Raises:
        exc: if mail could not be sent.
    """
    receivers_list = receivers if isinstance(receivers, list) else [receivers]

    log.info(f"sending mail to: {', '.join(receivers_list)}")
    try:
        smtp = yagmail.SMTP(
            user=smtp_sender,
            password=smtp_password,
            host=smtp_server,
            port=smtp_port,
            smtp_ssl=smtp_tls,
        )
        smtp.send(
            to=receivers_list,
            subject=subject,
            contents=yagmail.raw(message),
            attachments=attachments,
        )
        log.info("email sent successfully")
    except Exception as exc:
        log.error(f"something went wrong. {exc=}")
        raise

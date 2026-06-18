import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_HOST = os.environ.get("SMTP_HOST", "")
_PORT = int(os.environ.get("SMTP_PORT", "587"))
_USER = os.environ.get("SMTP_USER", "")
_PASS = os.environ.get("SMTP_PASS", "")
_FROM = os.environ.get("SMTP_FROM", _USER)


def _send(to: str, subject: str, body_html: str):
    if not _HOST or not _USER:
        logger.warning("SMTP nije konfiguriran — email nije poslan na %s", to)
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = _FROM
    msg["To"] = to
    msg.attach(MIMEText(body_html, "html", "utf-8"))
    try:
        with smtplib.SMTP(_HOST, _PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(_USER, _PASS)
            smtp.sendmail(_FROM, [to], msg.as_string())
        logger.info("Email poslan na %s: %s", to, subject)
    except Exception as e:
        logger.error("Greška slanja emaila na %s: %s", to, e)


def send_join_confirmation(to_email: str, first_name: str, event_title: str, event_date: str, location: str):
    subject = f"Prijava potvrđena: {event_title}"
    body = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#222;">
      <h2 style="color:#5a9e2f;">Prijava uspješna!</h2>
      <p>Hej <strong>{first_name}</strong>,</p>
      <p>Uspješno si se prijavio/la na događaj:</p>
      <div style="background:#f5f5f5;border-left:4px solid #5a9e2f;padding:12px 16px;margin:16px 0;border-radius:4px;">
        <strong style="font-size:1.1em;">{event_title}</strong><br>
        📅 {event_date}<br>
        📍 {location}
      </div>
      <p>Vidimo se tamo!</p>
      <p style="color:#888;font-size:0.85em;">— KvartStory tim</p>
    </div>
    """
    _send(to_email, subject, body)


def send_event_cancelled(to_email: str, first_name: str, event_title: str, event_date: str):
    subject = f"Otkazano: {event_title}"
    body = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#222;">
      <h2 style="color:#c0392b;">Događaj otkazan</h2>
      <p>Hej <strong>{first_name}</strong>,</p>
      <p>Nažalost, događaj na koji si bio/la prijavljen/a je otkazan:</p>
      <div style="background:#f5f5f5;border-left:4px solid #c0392b;padding:12px 16px;margin:16px 0;border-radius:4px;">
        <strong style="font-size:1.1em;">{event_title}</strong><br>
        📅 {event_date}
      </div>
      <p>Provjeri druge događaje na KvartStory platformi.</p>
      <p style="color:#888;font-size:0.85em;">— KvartStory tim</p>
    </div>
    """
    _send(to_email, subject, body)


def send_event_updated(to_email: str, first_name: str, event_title: str, event_date: str, location: str):
    subject = f"Promjena: {event_title}"
    body = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;padding:24px;color:#222;">
      <h2 style="color:#e67e22;">Događaj izmijenjen</h2>
      <p>Hej <strong>{first_name}</strong>,</p>
      <p>Događaj na koji si prijavljen/a je izmijenjen. Provjeri nove detalje:</p>
      <div style="background:#f5f5f5;border-left:4px solid #e67e22;padding:12px 16px;margin:16px 0;border-radius:4px;">
        <strong style="font-size:1.1em;">{event_title}</strong><br>
        📅 {event_date}<br>
        📍 {location}
      </div>
      <p style="color:#888;font-size:0.85em;">— KvartStory tim</p>
    </div>
    """
    _send(to_email, subject, body)

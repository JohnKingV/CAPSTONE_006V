# app/core/mailer.py
import os
import smtplib
import logging
from email.message import EmailMessage
from typing import Iterable, Optional
from pydantic import EmailStr

logger = logging.getLogger(__name__)

# ========================
# Config SMTP por entorno
# ========================
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))        # 587 típico STARTTLS, 465 SSL
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER or "")

# Control transporte
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "true").lower() in ("1", "true", "yes")

# Opcionales
SMTP_TIMEOUT = float(os.getenv("SMTP_TIMEOUT", "15"))
REPLY_TO = os.getenv("REPLY_TO", "")  # ej: "Soporte DiagnosticaDoc <soporte@tu-dominio.com>"

# ========================
# Builders de mensajes
# ========================
def build_email_confirmacion(to_email: EmailStr, data: dict) -> EmailMessage:
    """
    Email de confirmación de cita.
    data esperada:
      paciente_nombre, fecha, hora, doctor, especialidad, modalidad ('online'|'presencial'), motivo?, nro_reserva
    """
    modalidad_display = "Teleconsulta" if data.get("modalidad") == "online" else "Presencial"

    subject = f"Confirmación de cita – {data['fecha']} {data['hora']}"
    txt = (
        f"Hola {data['paciente_nombre']},\n\n"
        f"Tu cita fue agendada exitosamente.\n\n"
        f"Fecha: {data['fecha']} {data['hora']}\n"
        f"Doctor: {data['doctor']} ({data['especialidad']})\n"
        f"Modalidad: {modalidad_display}\n"
        f"Motivo: {data.get('motivo','')}\n"
        f"N° Reserva: {data['nro_reserva']}\n\n"
        "Si necesitas reprogramar, responde este correo.\n\n"
        "Saludos,\nDiagnosticaDoc"
    )
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;max-width:600px;margin:0 auto">
      <h2 style="margin:0 0 16px;color:#0B6AA3">Confirmación de cita</h2>
      <p>Hola <b>{data['paciente_nombre']}</b>,</p>
      <p>Tu cita fue agendada exitosamente.</p>
      <ul style="list-style:none;padding:0;margin:16px 0">
        <li style="margin:8px 0"><b>Fecha y hora:</b> {data['fecha']} {data['hora']}</li>
        <li style="margin:8px 0"><b>Doctor:</b> {data['doctor']} ({data['especialidad']})</li>
        <li style="margin:8px 0"><b>Modalidad:</b> {modalidad_display}</li>
        <li style="margin:8px 0"><b>Motivo:</b> {data.get('motivo','')}</li>
        <li style="margin:8px 0"><b>N° Reserva:</b> <code style="background:#f0f0f0;padding:2px 6px;border-radius:4px">{data['nro_reserva']}</code></li>
      </ul>
      <p>Si necesitas reprogramar, responde este correo.</p>
      <p>Saludos,<br><b>DiagnosticaDoc</b></p>
    </div>
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = str(to_email)
    if REPLY_TO:
        msg["Reply-To"] = REPLY_TO
    msg.set_content(txt)
    msg.add_alternative(html, subtype="html")
    return msg


def build_email_set_password(to_email: EmailStr, link: str) -> EmailMessage:
    """
    Email con el enlace para establecer contraseña (válido p.ej. 60 min).
    """
    subject = "Establecer contraseña — DiagnosticaDoc"
    txt = (
        "Has solicitado establecer tu contraseña en DiagnosticaDoc.\n\n"
        f"Enlace: {link}\n\n"
        "Este enlace expira en 60 minutos. Si no fuiste tú, ignora este correo."
    )
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;line-height:1.6;max-width:600px;margin:0 auto">
      <h2 style="margin:0 0 16px;color:#0B6AA3">Establecer contraseña</h2>
      <p>Has solicitado establecer tu contraseña en <b>DiagnosticaDoc</b>.</p>
      <p style="margin:16px 0">
        <a href="{link}" style="background:#0B6AA3;color:#fff;padding:10px 16px;border-radius:8px;text-decoration:none;display:inline-block">
          Establecer contraseña
        </a>
      </p>
      <p>Si el botón no funciona, copia y pega esta URL en tu navegador:</p>
      <p><code style="background:#f0f0f0;padding:2px 6px;border-radius:4px;word-break:break-all">{link}</code></p>
      <p style="color:#64748b;font-size:12px">Este enlace expira en 60 minutos. Si no fuiste tú, ignora este correo.</p>
      <p>Saludos,<br><b>DiagnosticaDoc</b></p>
    </div>
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = str(to_email)
    if REPLY_TO:
        msg["Reply-To"] = REPLY_TO
    msg.set_content(txt)
    msg.add_alternative(html, subtype="html")
    return msg


# ========================
# Envío SMTP genérico
# ========================
def send_email(
    msg: EmailMessage,
    *,
    bcc: Optional[Iterable[str]] = None,
) -> None:
    """
    Envía un email usando SMTP. Lanza RuntimeError ante error.
    - Usa STARTTLS por defecto (puedes forzar SSL con SMTP_USE_SSL=true y puerto 465).
    - Aplica timeout configurable.
    """
    # Validaciones mínimas
    if not SMTP_HOST or not SMTP_PORT or not FROM_EMAIL:
        error_msg = "SMTP no configurado: faltan SMTP_HOST/SMTP_PORT/FROM_EMAIL"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    if bcc:
        # BCC se agrega al envelope pero no al header "To"
        for addr in bcc:
            msg["Bcc"] = msg.get("Bcc", "")
            if msg["Bcc"]:
                msg.replace_header("Bcc", msg["Bcc"] + f",{addr}")
            else:
                msg["Bcc"] = addr

    # Log seguro (no exponemos password ni headers sensibles)
    logger.info(
        "SMTP send -> host=%s port=%s ssl=%s starttls=%s from=%s to=%s",
        SMTP_HOST, SMTP_PORT, SMTP_USE_SSL, SMTP_STARTTLS, FROM_EMAIL, msg.get("To"),
    )

    try:
        if SMTP_USE_SSL:
            # SSL directo (p.ej. puerto 465)
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as s:
                if SMTP_USER and SMTP_PASSWORD:
                    s.login(SMTP_USER, SMTP_PASSWORD)
                s.send_message(msg)
        else:
            # STARTTLS (p.ej. puerto 587) — recomendado por Gmail
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as s:
                if SMTP_STARTTLS:
                    s.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    s.login(SMTP_USER, SMTP_PASSWORD)
                s.send_message(msg)

        logger.info("Email enviado a %s", msg.get("To"))
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP al enviar a {msg.get('To','desconocido')}: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Error inesperado al enviar a {msg.get('To','desconocido')}: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e

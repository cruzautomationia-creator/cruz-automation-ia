import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

def enviar_email(destinatario, asunto, cuerpo_html):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "Credenciales SMTP no configuradas."
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = f"Cruz Automation IA <{SMTP_EMAIL}>"
        msg["To"] = destinatario
        msg.attach(MIMEText(cuerpo_html, "html"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())
        return True, "Email enviado."
    except Exception as e:
        return False, str(e)

def email_recordatorio_pago(nombre, email, monto, servicio, fecha_pago):
    asunto = f"Recordatorio de pago — {servicio}"
    cuerpo = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:24px;background:#f9f9f9;border-radius:12px;">
      <h2 style="color:#534AB7;">Cruz Automation IA</h2>
      <p>Hola <strong>{nombre}</strong>,</p>
      <p>Te recordamos que tu pago por <strong>{servicio}</strong> vence el <strong>{fecha_pago}</strong>.</p>
      <div style="background:#EEEDFE;padding:16px;border-radius:8px;margin:16px 0;">
        <p style="margin:0;font-size:18px;font-weight:bold;color:#3C3489;">Monto: ${monto}</p>
      </div>
      <p>Si ya realizaste el pago, ignora este mensaje.</p>
      <p style="color:#999;font-size:12px;">Cruz Automation IA</p>
    </div>"""
    return enviar_email(email, asunto, cuerpo)

def email_bienvenida(nombre, email, servicio, mensualidad):
    asunto = "¡Bienvenido a Cruz Automation IA!"
    cuerpo = f"""
    <div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:24px;background:#f9f9f9;border-radius:12px;">
      <h2 style="color:#534AB7;">¡Bienvenido, {nombre}!</h2>
      <p>Estamos felices de tenerte como cliente de <strong>Cruz Automation IA</strong>.</p>
      <div style="background:#EEEDFE;padding:16px;border-radius:8px;margin:16px 0;">
        <p style="margin:0;"><strong>Servicio:</strong> {servicio}</p>
        <p style="margin:8px 0 0;"><strong>Mensualidad:</strong> ${mensualidad}/mes</p>
      </div>
      <p>¡Vamos a hacer crecer tu negocio!</p>
      <p style="color:#999;font-size:12px;">Cruz Automation IA</p>
    </div>"""
    return enviar_email(email, asunto, cuerpo)

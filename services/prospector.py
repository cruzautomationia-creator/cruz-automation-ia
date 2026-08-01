import argparse
import sys
import os
import imaplib
import email as email_lib
import urllib.parse
from email.header import decode_header

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services import ai, notifications

LIMITE_DIARIO_DEFECTO = 25
MINIMO_DIARIO_OBJETIVO = 20


def ya_contactado(nombre, email):
    existentes = db.obtener_prospectos()
    nombre_l = (nombre or "").strip().lower()
    email_l = (email or "").strip().lower()
    for p in existentes:
        if email_l and (p.get("email") or "").strip().lower() == email_l:
            return True
        if nombre_l and (p.get("nombre") or "").strip().lower() == nombre_l:
            return True
    return False


def _leads_de_hoy():
    from datetime import date
    hoy = date.today().isoformat()
    existentes = db.obtener_prospectos()
    return [p for p in existentes if p.get("canal") == "Agente de Prospección" and str(p.get("created_at", "")).startswith(hoy)]


def contactados_hoy():
    return len(_leads_de_hoy())


def enviar_resumen_diario():
    """Manda un email de resumen a la propia empresa avisando que el trabajo del día está listo."""
    destino = os.environ.get("SMTP_EMAIL")
    if not destino:
        print("Sin SMTP_EMAIL configurado, no se puede enviar el resumen.")
        return

    leads = _leads_de_hoy()
    con_whatsapp = [p for p in leads if p.get("whatsapp")]
    con_email = [p for p in leads if p.get("email")]

    filas = "".join(
        f"<li><b>{p['nombre']}</b> — {p.get('pais','')} "
        f"{'📱 WhatsApp listo' if p.get('whatsapp') else ''} "
        f"{'📧 Email enviado' if p.get('email') else ''}</li>"
        for p in leads
    )
    cuerpo = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;background:#f9f9f9;border-radius:12px;">
      <h2 style="color:#534AB7;margin:0 0 16px;">✅ Prospección de hoy lista</h2>
      <p>El agente terminó de trabajar. Resumen de hoy:</p>
      <div style="background:#EEEDFE;padding:16px;border-radius:8px;margin:16px 0;">
        <p style="margin:0;"><b>{len(leads)}</b> negocios contactados en total</p>
        <p style="margin:4px 0 0;"><b>{len(con_email)}</b> por email (ya enviados)</p>
        <p style="margin:4px 0 0;"><b>{len(con_whatsapp)}</b> con WhatsApp listo para que apruebes con un clic</p>
      </div>
      <p><b>Entra a la app → Prospectos y dale "Enviar por WhatsApp" a los que quieras.</b></p>
      <ul style="line-height:1.8;">{filas}</ul>
      <p style="color:#999;font-size:12px;margin-top:20px;">Cruz Automation IA · Agente de Prospección</p>
    </div>"""
    ok, msg = notifications.enviar_email(destino, f"✅ Prospección lista: {len(leads)} negocios contactados hoy", cuerpo)
    print(f"Resumen diario: {'enviado' if ok else 'FALLO - ' + msg}")


def _decodificar(valor):
    partes = decode_header(valor or "")
    resultado = ""
    for texto, codificacion in partes:
        if isinstance(texto, bytes):
            resultado += texto.decode(codificacion or "utf-8", errors="ignore")
        else:
            resultado += texto
    return resultado


def _texto_plano(msg):
    if msg.is_multipart():
        for parte in msg.walk():
            if parte.get_content_type() == "text/plain" and not parte.get("Content-Disposition"):
                try:
                    return parte.get_payload(decode=True).decode(parte.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    continue
        return ""
    try:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
    except Exception:
        return ""


def revisar_respuestas():
    """Revisa el inbox de Gmail buscando respuestas de leads contactados por el agente, clasifica y actualiza su estado."""
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    if not smtp_email or not smtp_password:
        print("Sin credenciales de Gmail configuradas, no se pueden revisar respuestas.")
        return

    prospectos = db.obtener_prospectos()
    por_email = {}
    for p in prospectos:
        e = (p.get("email") or "").strip().lower()
        if e and p.get("canal") == "Agente de Prospección" and p.get("estado") == "nuevo":
            por_email[e] = p

    if not por_email:
        print("No hay prospectos pendientes de revisión de respuesta.")
        return

    try:
        conn = imaplib.IMAP4_SSL("imap.gmail.com")
        conn.login(smtp_email, smtp_password)
        conn.select("INBOX")
        estado_busqueda, datos = conn.search(None, "UNSEEN")
        ids = datos[0].split() if estado_busqueda == "OK" else []
    except Exception as e:
        print(f"No se pudo conectar al inbox: {e}")
        return

    revisados = 0
    for msg_id in ids:
        try:
            _, datos_msg = conn.fetch(msg_id, "(RFC822)")
            crudo = datos_msg[0][1]
            msg = email_lib.message_from_bytes(crudo)
            remitente = email_lib.utils.parseaddr(msg.get("From", ""))[1].strip().lower()
            if remitente not in por_email:
                continue
            prospecto = por_email[remitente]
            cuerpo = _texto_plano(msg).strip()
            if not cuerpo:
                continue

            clasif = ai.clasificar_respuesta(prospecto["nombre"], cuerpo[:2000])
            nuevo_estado = {
                "interesado": "en_negociacion",
                "pidio_info": "en_negociacion",
                "no_interesado": "descartado",
                "fuera_de_tema": "nuevo",
            }.get(clasif.get("clasificacion"), "nuevo")

            db.actualizar_estado_prospecto(prospecto["id"], nuevo_estado)
            nota_extra = f"\n\n[Respuesta recibida] {clasif.get('clasificacion')}: {clasif.get('resumen')}\nSugerencia: {clasif.get('siguiente_paso_sugerido')}"
            db.actualizar_notas_prospecto(prospecto["id"], (prospecto.get("notas") or "") + nota_extra)
            print(f"Respuesta de {prospecto['nombre']} clasificada como '{clasif.get('clasificacion')}' -> estado: {nuevo_estado}")
            revisados += 1
        except Exception as e:
            print(f"Error procesando mensaje: {e}")

    conn.logout()
    print(f"Revisión de respuestas completa. {revisados} respuestas procesadas.")


def agregar_lead(nombre, pais, debilidad, email=None, whatsapp=None, servicio_sugerido=None, limite_diario=LIMITE_DIARIO_DEFECTO):
    if ya_contactado(nombre, email):
        print(f"OMITIDO (ya contactado antes): {nombre}")
        return {"omitido": True, "razon": "ya_contactado"}

    outreach = ai.redactar_outreach(nombre, pais, debilidad, tiene_whatsapp=bool(whatsapp))

    email_enviado = False
    if email:
        ok, msg = notifications.enviar_email(email, outreach["asunto_email"], _html_email(outreach["cuerpo_email"], nombre))
        email_enviado = ok
        print(f"Email a {nombre} <{email}>: {'OK' if ok else 'FALLO - ' + msg}")
    else:
        print(f"Sin email para {nombre}, solo se guarda el prospecto y el borrador de WhatsApp.")

    notas = f"[Detectado por Agente de Prospección] Debilidad: {debilidad}."
    if outreach.get("portafolio_usado"):
        notas += f"\nEjemplo de portafolio incluido: {outreach['portafolio_usado']}"
    if whatsapp:
        numero_limpio = "".join(c for c in whatsapp if c.isdigit())
        link_whatsapp = f"https://wa.me/{numero_limpio}?text={urllib.parse.quote(outreach['mensaje_whatsapp'])}"
        notas += f"\n\nWHATSAPP_LINK::{link_whatsapp}"
        notas += f"\n\nBorrador de WhatsApp:\n{outreach['mensaje_whatsapp']}"
    if not email_enviado:
        notas += "\n\n(No se envió email automático: sin dirección de correo o fallo de envío.)"

    db.agregar_prospecto(
        nombre=nombre,
        email=email,
        whatsapp=whatsapp,
        pais=pais,
        servicio_interes=servicio_sugerido or "Por definir",
        presupuesto=None,
        canal="Agente de Prospección",
        notas=notas,
    )
    print(f"Prospecto guardado: {nombre} ({pais})")
    return {"omitido": False, "email_enviado": email_enviado, "whatsapp_borrador": outreach.get("mensaje_whatsapp")}


NUMERO_EMPRESA = "56972446549"

def _link_whatsapp_empresa(nombre_negocio):
    mensaje = f"Hola! Vi el correo de Cruz Automation IA sobre {nombre_negocio} y quiero saber más."
    return f"https://wa.me/{NUMERO_EMPRESA}?text={urllib.parse.quote(mensaje)}"


def _html_email(cuerpo_texto, nombre_negocio=""):
    parrafos_lista = [p for p in cuerpo_texto.split("\n") if p.strip()]
    gancho = parrafos_lista[0] if parrafos_lista else ""
    resto = parrafos_lista[1:] if len(parrafos_lista) > 1 else []
    resto_html = "".join(f"<p style='margin:0 0 14px;line-height:1.65;color:#2b2b3a;font-size:15px;'>{p}</p>" for p in resto)
    link_wa = _link_whatsapp_empresa(nombre_negocio)
    return f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:540px;margin:auto;background:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 8px 30px rgba(83,74,183,0.15);border:1px solid #EEEEF8;">
      <div style="background:linear-gradient(135deg,#6C63E8,#534AB7);padding:28px 28px 22px;">
        <div style="color:#fff;font-size:13px;font-weight:700;letter-spacing:1px;opacity:.85;text-transform:uppercase;">⚡ Cruz Automation IA</div>
        <div style="color:#fff;font-size:20px;font-weight:800;margin-top:8px;line-height:1.35;">👀 Algo llamó nuestra atención sobre {nombre_negocio or 'tu negocio'}...</div>
      </div>
      <div style="padding:26px 28px 8px;">
        <p style="margin:0 0 16px;line-height:1.65;font-size:16px;font-weight:600;color:#23262f;">{gancho}</p>
        {resto_html}
      </div>
      <div style="text-align:center;margin:20px 28px 28px;">
        <a href="{link_wa}" style="background:#25D366;color:#fff;text-decoration:none;padding:14px 30px;border-radius:30px;font-weight:800;font-size:15.5px;display:inline-block;box-shadow:0 6px 18px rgba(37,211,102,0.4);">💬 Escríbenos por WhatsApp ahora</a>
      </div>
      <div style="background:#F8F8FC;padding:16px 28px;text-align:center;border-top:1px solid #EEEEF8;">
        <p style="color:#9aa2b6;font-size:12px;margin:0;">Cruz Automation IA · cruzautomationia@gmail.com · +56 9 7244 6549</p>
      </div>
    </div>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente de prospección de Cruz Automation IA.")
    subparsers = parser.add_subparsers(dest="comando")

    p_lead = subparsers.add_parser("agregar-lead", help="Agrega y contacta un lead encontrado.")
    p_lead.add_argument("--nombre", required=True)
    p_lead.add_argument("--pais", required=True)
    p_lead.add_argument("--debilidad", required=True, help="Ej: 'no tiene sitio web', 'Instagram inactivo hace meses'")
    p_lead.add_argument("--email", default=None)
    p_lead.add_argument("--whatsapp", default=None)
    p_lead.add_argument("--servicio", default=None)

    subparsers.add_parser("revisar-respuestas", help="Revisa el inbox de Gmail y clasifica respuestas de leads.")
    subparsers.add_parser("contactados-hoy", help="Muestra cuántos leads se han contactado hoy.")
    subparsers.add_parser("resumen-diario", help="Envía un email de resumen avisando que el trabajo de hoy está listo.")

    args = parser.parse_args()

    if args.comando == "revisar-respuestas":
        revisar_respuestas()
    elif args.comando == "contactados-hoy":
        print(contactados_hoy())
    elif args.comando == "resumen-diario":
        enviar_resumen_diario()
    elif args.comando == "agregar-lead":
        if contactados_hoy() >= LIMITE_DIARIO_DEFECTO:
            print(f"Tope de seguridad de {LIMITE_DIARIO_DEFECTO} contactos alcanzado hoy. No se procesa este lead.")
            sys.exit(0)
        agregar_lead(args.nombre, args.pais, args.debilidad, email=args.email, whatsapp=args.whatsapp, servicio_sugerido=args.servicio)
    else:
        parser.print_help()

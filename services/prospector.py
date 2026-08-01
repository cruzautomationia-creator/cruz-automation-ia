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


def contactados_hoy():
    from datetime import date
    hoy = date.today().isoformat()
    existentes = db.obtener_prospectos()
    return sum(1 for p in existentes if p.get("canal") == "Agente de Prospección" and str(p.get("created_at", "")).startswith(hoy))


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
        ok, msg = notifications.enviar_email(email, outreach["asunto_email"], _html_email(outreach["cuerpo_email"]))
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


def _html_email(cuerpo_texto):
    parrafos = "".join(f"<p style='margin:0 0 12px;line-height:1.6;'>{p}</p>" for p in cuerpo_texto.split("\n") if p.strip())
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;background:#f9f9f9;border-radius:12px;">
      <h2 style="color:#534AB7;margin:0 0 16px;">Cruz Automation IA</h2>
      {parrafos}
      <p style="color:#999;font-size:12px;margin-top:20px;">Cruz Automation IA · cruzautomationia@gmail.com · +56 9 7244 6549</p>
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

    args = parser.parse_args()

    if args.comando == "revisar-respuestas":
        revisar_respuestas()
    elif args.comando == "contactados-hoy":
        print(contactados_hoy())
    elif args.comando == "agregar-lead":
        if contactados_hoy() >= LIMITE_DIARIO_DEFECTO:
            print(f"Tope de seguridad de {LIMITE_DIARIO_DEFECTO} contactos alcanzado hoy. No se procesa este lead.")
            sys.exit(0)
        agregar_lead(args.nombre, args.pais, args.debilidad, email=args.email, whatsapp=args.whatsapp, servicio_sugerido=args.servicio)
    else:
        parser.print_help()

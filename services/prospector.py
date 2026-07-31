import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from services import ai, notifications

LIMITE_DIARIO_DEFECTO = 20


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
    if whatsapp:
        notas += f"\n\nBorrador de WhatsApp (enviar manualmente):\n{outreach['mensaje_whatsapp']}"
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
    parser = argparse.ArgumentParser(description="Agrega y contacta un lead encontrado por el agente de prospección.")
    parser.add_argument("--nombre", required=True)
    parser.add_argument("--pais", required=True)
    parser.add_argument("--debilidad", required=True, help="Ej: 'no tiene sitio web', 'Instagram inactivo hace meses'")
    parser.add_argument("--email", default=None)
    parser.add_argument("--whatsapp", default=None)
    parser.add_argument("--servicio", default=None)
    args = parser.parse_args()

    if contactados_hoy() >= LIMITE_DIARIO_DEFECTO:
        print(f"Límite diario de {LIMITE_DIARIO_DEFECTO} contactos alcanzado. No se procesa este lead hoy.")
        sys.exit(0)

    agregar_lead(args.nombre, args.pais, args.debilidad, email=args.email, whatsapp=args.whatsapp, servicio_sugerido=args.servicio)

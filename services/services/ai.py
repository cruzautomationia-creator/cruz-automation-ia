import anthropic
import os
import json

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no está configurada.")
    return anthropic.Anthropic(api_key=api_key)

def generar_contenido_marketing(nicho, contexto):
    client = get_client()
    prompt = f"""Eres el agente de marketing de Cruz Automation IA.
Genera contenido para un cliente con estas características:
Nicho: {nicho}
Contexto: {contexto}

Responde SOLO en JSON válido:
{{
  "carruseles": [
    {{"titulo": "...", "slides": ["slide 1", "slide 2", "slide 3", "slide 4", "slide 5"]}},
    {{"titulo": "...", "slides": ["slide 1", "slide 2", "slide 3", "slide 4", "slide 5"]}},
    {{"titulo": "...", "slides": ["slide 1", "slide 2", "slide 3", "slide 4", "slide 5"]}}
  ],
  "guion_reel": {{"hook": "...", "desarrollo": "...", "cta": "..."}},
  "estrategia_semanal": {{"lunes": "...", "miercoles": "...", "viernes": "...", "domingo": "..."}},
  "ideas_virales": ["idea 1", "idea 2", "idea 3"]
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def investigar_tendencias():
    client = get_client()
    prompt = """Eres el agente de investigación de Cruz Automation IA.
Genera tendencias actuales en automatización IA y marketing digital para Latinoamérica.

Responde SOLO en JSON válido:
{
  "tendencias": [
    {"titulo": "...", "descripcion": "...", "oportunidad": "...", "nivel": "alta"}
  ],
  "resumen": "...",
  "accion_inmediata": "..."
}
Genera 5 tendencias."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def analizar_finanzas(ingresos, pendientes, meta, num_clientes, servicios):
    client = get_client()
    prompt = f"""Eres el agente financiero de Cruz Automation IA.
Ingresos confirmados: ${ingresos}
Cobros pendientes: ${pendientes}
Meta mensual: ${meta}
Clientes activos: {num_clientes}
Servicios: {servicios}

Responde SOLO en JSON:
{{
  "diagnostico": "...",
  "estrategias": ["estrategia 1", "estrategia 2", "estrategia 3"],
  "proyeccion_3_meses": "...",
  "accion_hoy": "..."
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def generar_mensaje_cobro(nombre, monto, servicio, dias_vencido=0):
    client = get_client()
    contexto = f"vencido hace {dias_vencido} días" if dias_vencido > 0 else "próximo a vencer"
    prompt = f"""Genera un mensaje de cobro profesional y amigable para WhatsApp.
Cliente: {nombre}
Monto: ${monto}
Servicio: {servicio}
Estado: {contexto}
Máximo 5 líneas. Solo el mensaje."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

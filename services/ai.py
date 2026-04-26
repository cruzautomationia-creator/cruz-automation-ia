import anthropic
import os
import json

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no está configurada.")
    return anthropic.Anthropic(api_key=api_key)

def investigar_tendencias():
    client = get_client()
    prompt = """Eres el agente de investigación de Cruz Automation IA, agencia digital en Latinoamérica especializada en webs, automatizaciones y contenido.

Investiga tendencias actuales en:
- Automatización IA para negocios
- Marketing digital en redes sociales
- Herramientas emergentes para agencias digitales

Responde SOLO en JSON válido:
{
  "tendencias": [
    {"titulo": "...", "descripcion": "...", "oportunidad": "...", "nivel": "alta"}
  ],
  "resumen": "...",
  "accion_inmediata": "..."
}
Genera 5 tendencias relevantes para una agencia en Latinoamérica."""
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
Ingresos confirmados este mes: ${ingresos}
Cobros pendientes: ${pendientes}
Meta mensual: ${meta}
Clientes activos: {num_clientes}
Servicios ofrecidos: {servicios}

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
Máximo 5 líneas. Solo el mensaje, sin explicaciones."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def generar_plan_contenido(cliente_nombre, servicio, mes):
    client = get_client()
    prompt = f"""Eres el agente de planificación de contenido de Cruz Automation IA.
Cliente: {cliente_nombre}
Servicio contratado: {servicio}
Mes a planificar: {mes}

Genera un plan de contenido mensual organizado por semanas.
Responde SOLO en JSON:
{{
  "semana_1": [
    {{"dia": "Lunes", "tipo": "...", "tema": "...", "formato": "video|imagen|carrusel|story"}},
    {{"dia": "Miércoles", "tipo": "...", "tema": "...", "formato": "video|imagen|carrusel|story"}},
    {{"dia": "Viernes", "tipo": "...", "tema": "...", "formato": "video|imagen|carrusel|story"}}
  ],
  "semana_2": [...],
  "semana_3": [...],
  "semana_4": [...],
  "estrategia_general": "..."
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

import anthropic
import os
import json

EMPRESA_INFO = """
Empresa: Cruz Automation IA
Web: cruzautomationia.com
Servicios: Páginas web personalizadas y automatización de redes sociales
País: Chile, trabajo 100% remoto con clientes de todo el mundo

PRECIOS Y COMBOS:
- Combo Lanzamiento: $120 USD (Landing page + Bot WhatsApp starter + 30 días soporte)
- Combo Presencia Digital: $300 USD (Web corporativa + Bot WhatsApp completo + Bot Instagram)
- Combo Redes Completas: $130 USD (Bot Instagram + Bot TikTok + Email marketing)
- Combo Tienda Completa: $480 USD (E-commerce hasta 50 productos + Automatización 4 plataformas)
- Servicios desde: $100 USD

TIEMPOS DE ENTREGA:
- Landing Page: 3-5 días
- Portafolio: 5-7 días
- Web Corporativa: 7-10 días
- E-commerce: 10-15 días
- Automatización de Redes: 3-7 días

FORMA DE PAGO: 50% al inicio + 50% al entregar
MENSUALIDAD DE MANTENIMIENTO: Variable según cliente
CONTACTO: +56 9 7244 6549 | cruzautomationia@gmail.com
"""

def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no está configurada.")
    return anthropic.Anthropic(api_key=api_key)

def investigar_tendencias():
    client = get_client()
    prompt = f"""Eres el agente de investigación de Cruz Automation IA.

{EMPRESA_INFO}

Investiga y genera un reporte de tendencias ACTUALES (2026) en:
- Automatización IA para negocios en Latinoamérica
- Marketing digital y redes sociales
- Diseño web y e-commerce
- Herramientas y tecnologías emergentes

Responde SOLO en JSON válido:
{{
  "tendencias": [
    {{
      "titulo": "...",
      "descripcion": "...",
      "oportunidad": "...",
      "accion_concreta": "...",
      "nivel": "alta|media|baja",
      "fuente": "..."
    }}
  ],
  "resumen": "...",
  "accion_inmediata": "..."
}}
Genera 5 tendencias con oportunidades concretas para Cruz Automation IA."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def analizar_finanzas(ingresos, pendientes, meta, num_clientes, servicios):
    client = get_client()
    prompt = f"""Eres el agente financiero de Cruz Automation IA.

{EMPRESA_INFO}

Datos actuales:
- Ingresos confirmados este mes: ${ingresos}
- Cobros pendientes: ${pendientes}
- Meta mensual: ${meta}
- Clientes activos: {num_clientes}
- Servicios ofrecidos: {servicios}

Analiza la situación y responde SOLO en JSON:
{{
  "diagnostico": "...",
  "estrategias": ["estrategia 1", "estrategia 2", "estrategia 3"],
  "proyeccion_3_meses": "...",
  "accion_hoy": "...",
  "precio_recomendado": "..."
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def generar_cotizacion(descripcion_proyecto, nombre_cliente, pais):
    client = get_client()
    prompt = f"""Eres el agente de precios de Cruz Automation IA.

{EMPRESA_INFO}

Cliente: {nombre_cliente} de {pais}
Proyecto solicitado: {descripcion_proyecto}

Genera una cotización profesional. Responde SOLO en JSON:
{{
  "combo_recomendado": "...",
  "precio_base": 0,
  "precio_final": 0,
  "descuento": 0,
  "incluye": ["item 1", "item 2", "item 3"],
  "no_incluye": ["item 1", "item 2"],
  "tiempo_entrega": "...",
  "mensualidad_sugerida": 0,
  "justificacion": "...",
  "alternativa_economica": "...",
  "alternativa_premium": "..."
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def generar_propuesta(nombre_cliente, pais, servicio, presupuesto, notas):
    client = get_client()
    prompt = f"""Eres el agente de propuestas de Cruz Automation IA.

{EMPRESA_INFO}

Genera una propuesta comercial profesional para:
- Cliente: {nombre_cliente}
- País: {pais}
- Servicio solicitado: {servicio}
- Presupuesto mencionado: {presupuesto}
- Notas adicionales: {notas}

La propuesta debe ser profesional, persuasiva y usar los precios reales de Cruz Automation IA.

Responde SOLO en JSON:
{{
  "asunto": "...",
  "saludo": "...",
  "introduccion": "...",
  "propuesta_servicio": "...",
  "precio": "...",
  "incluye": ["item 1", "item 2", "item 3", "item 4"],
  "tiempo_entrega": "...",
  "forma_pago": "50% al inicio ($X USD) + 50% al entregar ($X USD)",
  "proximos_pasos": "...",
  "cierre": "...",
  "firma": "Cruz Automation IA\\ncruzautomationia@gmail.com\\n+56 9 7244 6549"
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def generar_acuerdo(nombre_cliente, email_cliente, pais, servicio, monto_total, incluye, fecha_inicio):
    client = get_client()
    prompt = f"""Eres el agente de acuerdos de Cruz Automation IA.

{EMPRESA_INFO}

Genera un acuerdo de servicio profesional para:
- Cliente: {nombre_cliente}
- Email: {email_cliente}
- País: {pais}
- Servicio: {servicio}
- Monto total: ${monto_total} USD
- Incluye: {incluye}
- Fecha de inicio: {fecha_inicio}

Responde SOLO en JSON:
{{
  "titulo": "ACUERDO DE SERVICIO DIGITAL",
  "partes": "...",
  "servicio_acordado": "...",
  "incluye": ["item 1", "item 2", "item 3"],
  "no_incluye": ["item 1", "item 2"],
  "monto": "${monto_total} USD",
  "forma_pago": "50% al inicio (${monto_total/2} USD) + 50% al entregar (${monto_total/2} USD)",
  "tiempo_entrega": "...",
  "revisiones": "...",
  "cancelacion": "...",
  "propiedad": "...",
  "confidencialidad": "...",
  "fecha": "{fecha_inicio}",
  "firma_proveedor": "Cruz Automation IA — cruzautomationia@gmail.com"
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def generar_mensaje_cobro(nombre, monto, servicio, tipo="mensualidad", dias_vencido=0):
    client = get_client()
    contexto = f"vencido hace {dias_vencido} días" if dias_vencido > 0 else "próximo a vencer"
    prompt = f"""Genera un mensaje de cobro profesional y amigable para WhatsApp.
Empresa que cobra: Cruz Automation IA
Cliente: {nombre}
Monto: ${monto} USD
Servicio: {servicio}
Tipo de cobro: {tipo}
Estado: {contexto}

El mensaje debe ser corto, directo, respetuoso y con tono cercano. Máximo 6 líneas. Solo el mensaje."""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def generar_plan_contenido(cliente_nombre, servicio, mes):
    client = get_client()
    prompt = f"""Eres el agente de planificación de Cruz Automation IA.

{EMPRESA_INFO}

Cliente: {cliente_nombre}
Servicio contratado: {servicio}
Mes: {mes}

Genera un plan de contenido mensual organizado por semanas.
Responde SOLO en JSON:
{{
  "semana_1": [
    {{"dia": "Lunes", "tipo": "...", "tema": "...", "formato": "video|imagen|carrusel|story"}}
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

def generar_bienvenida(nombre_cliente, email_cliente, servicio, monto_inicial):
    client = get_client()
    prompt = f"""Genera un correo de bienvenida profesional de Cruz Automation IA para un cliente nuevo.

Cliente: {nombre_cliente}
Email: {email_cliente}
Servicio contratado: {servicio}
Pago inicial recibido: ${monto_inicial} USD

El correo debe ser cálido, profesional y explicar los próximos pasos claramente.
Responde SOLO en JSON:
{{
  "asunto": "...",
  "cuerpo": "..."
}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    text = message.content[0].text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)

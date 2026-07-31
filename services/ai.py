from groq import Groq
import os
import json

MODEL = "llama-3.3-70b-versatile"

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
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no está configurada.")
    return Groq(api_key=api_key)

def _completar(prompt, max_tokens, json_mode=True):
    client = get_client()
    kwargs = {"type": "json_object"} if json_mode else None
    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        response_format=kwargs,
    )
    return completion.choices[0].message.content.strip()

def _completar_json(prompt, max_tokens):
    text = _completar(prompt, max_tokens, json_mode=True)
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def investigar_tendencias():
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
    return _completar_json(prompt, 2000)

def analizar_finanzas(ingresos, pendientes, meta, num_clientes, servicios):
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
    return _completar_json(prompt, 1000)

def generar_cotizacion(descripcion_proyecto, nombre_cliente, pais):
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
    return _completar_json(prompt, 1000)

def generar_propuesta(nombre_cliente, pais, servicio, presupuesto, notas):
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
    return _completar_json(prompt, 1500)

def generar_acuerdo(nombre_cliente, email_cliente, pais, servicio, monto_total, incluye, fecha_inicio):
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
    return _completar_json(prompt, 1500)

def generar_mensaje_cobro(nombre, monto, servicio, tipo="mensualidad", dias_vencido=0):
    contexto = f"vencido hace {dias_vencido} días" if dias_vencido > 0 else "próximo a vencer"
    prompt = f"""Genera un mensaje de cobro profesional y amigable para WhatsApp.
Empresa que cobra: Cruz Automation IA
Cliente: {nombre}
Monto: ${monto} USD
Servicio: {servicio}
Tipo de cobro: {tipo}
Estado: {contexto}

El mensaje debe ser corto, directo, respetuoso y con tono cercano. Máximo 6 líneas. Solo el mensaje, sin JSON ni comillas."""
    return _completar(prompt, 300, json_mode=False)

def generar_plan_contenido(cliente_nombre, servicio, mes):
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
    return _completar_json(prompt, 2000)

PORTAFOLIO = [
    {"nombre": "Santiago Cruz Beauty Salon", "rubro": "salón de belleza, peluquería, uñas, maquillaje", "url": "https://tqraty.readdy.co"},
    {"nombre": "Santiago Cruz Aesthetic Studio", "rubro": "centro de estética, spa, bienestar, tratamientos faciales/corporales", "url": "https://xsjyhk.readdy.co"},
    {"nombre": "Santiago Cruz Dental Studio", "rubro": "clínica dental, odontología estética", "url": "https://mxcitf.readdy.co"},
    {"nombre": "Santiago Cruz Veterinary Center", "rubro": "veterinaria, clínica de mascotas", "url": "https://sdwjmz.readdy.co"},
    {"nombre": "Santiago Cruz Barbería (Quilpué)", "rubro": "barbería, peluquería masculina", "url": "https://xagtrs.readdy.co"},
    {"nombre": "Santiago Cruz Barbería", "rubro": "barbería, peluquería masculina", "url": "https://ziuwmz.readdy.co"},
    {"nombre": "Cruz Construcción (Madrid)", "rubro": "construcción, arquitectura, inmobiliaria, obra premium", "url": "https://tliohv.readdy.co"},
]

def redactar_outreach(nombre_negocio, pais, debilidad_detectada, tiene_whatsapp):
    catalogo_portafolio = "\n".join(f"- {p['nombre']} ({p['rubro']}): {p['url']}" for p in PORTAFOLIO)
    prompt = f"""Eres el agente de prospección de Cruz Automation IA.

{EMPRESA_INFO}

Vas a redactar un primer contacto en frío (cold outreach) para un negocio que encontraste investigando.

Negocio: {nombre_negocio}
País: {pais}
Debilidad detectada en su presencia digital: {debilidad_detectada}

PORTAFOLIO DISPONIBLE (ejemplos reales de sitios que hemos hecho, uno por rubro):
{catalogo_portafolio}

Reglas:
- Tono profesional, cercano, breve. Nada de sonar a plantilla genérica ni a spam.
- Menciona la debilidad detectada de forma específica y respetuosa (no ofensiva).
- Ofrece un servicio concreto de Cruz Automation IA que resuelva esa debilidad, con precio real.
- Termina invitando a una llamada/reunión corta, sin presionar.
- El email DEBE incluir al final una línea de salida clara tipo: "Si prefieres que no te vuelva a escribir, solo responde 'no' y no insistiré."
- El mensaje de whatsapp debe ser mucho mas corto que el email (maximo 4 lineas), mismo tono.
- PORTAFOLIO: revisa el rubro del negocio contactado contra el catálogo. Si hay un ejemplo del MISMO rubro o uno muy cercano/relacionado, incluye su link en el email (y opcionalmente en el whatsapp) invitando a verlo como muestra de trabajo real en su industria. Si NINGUNO del catálogo tiene relación real con el rubro del negocio, NO incluyas ningún link de portafolio — es mejor no mandar nada que mandar un ejemplo que no tiene sentido para ellos.

Responde SOLO en JSON:
{{
  "asunto_email": "...",
  "cuerpo_email": "...",
  "mensaje_whatsapp": "...",
  "portafolio_usado": "url del ejemplo usado, o null si no aplicó ninguno"
}}"""
    return _completar_json(prompt, 1000)

def generar_bienvenida(nombre_cliente, email_cliente, servicio, monto_inicial):
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
    return _completar_json(prompt, 800)

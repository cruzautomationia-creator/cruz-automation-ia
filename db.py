import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    pass

def agregar_prospecto(nombre, email, whatsapp, pais, servicio_interes, presupuesto, canal, notas):
    sb = get_client()
    sb.table("prospectos").insert({"nombre": nombre, "email": email, "whatsapp": whatsapp, "pais": pais, "servicio_interes": servicio_interes, "presupuesto": presupuesto, "canal": canal, "notas": notas}).execute()

def obtener_prospectos():
    sb = get_client()
    res = sb.table("prospectos").select("*").execute()
    return res.data or []

def actualizar_estado_prospecto(prospecto_id, estado):
    sb = get_client()
    sb.table("prospectos").update({"estado": estado}).eq("id", prospecto_id).execute()

def eliminar_prospecto(prospecto_id):
    sb = get_client()
    sb.table("prospectos").delete().eq("id", prospecto_id).execute()

def agregar_cliente(nombre, email, whatsapp, pais, servicio, mensualidad, fecha_pago, estado, notas, tipo_proyecto, monto_proyecto, pago_inicial, pago_final, estado_proyecto):
    sb = get_client()
    sb.table("clientes").insert({"nombre": nombre, "email": email, "whatsapp": whatsapp, "pais": pais, "servicio": servicio, "mensualidad": mensualidad, "fecha_pago": fecha_pago, "estado": estado, "notas": notas, "tipo_proyecto": tipo_proyecto, "monto_proyecto": monto_proyecto, "pago_inicial": pago_inicial, "pago_final": pago_final, "estado_proyecto": estado_proyecto}).execute()

def obtener_clientes():
    sb = get_client()
    res = sb.table("clientes").select("*").execute()
    return res.data or []

def actualizar_estado_cliente(cliente_id, nuevo_estado):
    sb = get_client()
    sb.table("clientes").update({"estado": nuevo_estado}).eq("id", cliente_id).execute()

def actualizar_estado_proyecto(cliente_id, estado_proyecto):
    sb = get_client()
    sb.table("clientes").update({"estado_proyecto": estado_proyecto}).eq("id", cliente_id).execute()

def registrar_pago_inicial(cliente_id, monto):
    sb = get_client()
    sb.table("clientes").update({"pago_inicial": monto, "estado_proyecto": "en_proceso"}).eq("id", cliente_id).execute()

def registrar_pago_final(cliente_id, monto):
    sb = get_client()
    sb.table("clientes").update({"pago_final": monto, "estado_proyecto": "entregado"}).eq("id", cliente_id).execute()

def eliminar_cliente(cliente_id):
    sb = get_client()
    sb.table("clientes").delete().eq("id", cliente_id).execute()

def registrar_pago(cliente_id, monto, fecha, metodo, notas):
    sb = get_client()
    sb.table("pagos").insert({"cliente_id": cliente_id, "monto": monto, "fecha": fecha, "metodo": metodo, "notas": notas}).execute()

def obtener_pagos():
    sb = get_client()
    res = sb.table("pagos").select("*, clientes(nombre)").execute()
    pagos = []
    for p in res.data or []:
        p["cliente_nombre"] = p.get("clientes", {}).get("nombre", "Sin cliente") if p.get("clientes") else "Sin cliente"
        pagos.append(p)
    return pagos

def ingresos_del_mes(mes):
    sb = get_client()
    res = sb.table("pagos").select("monto, fecha").execute()
    data = [p for p in res.data or [] if str(p.get("fecha", "")).startswith(mes)]
    return sum(p["monto"] for p in data)

def guardar_contenido(cliente_id, tipo, nicho, contenido):
    sb = get_client()
    sb.table("contenido_generado").insert({"cliente_id": cliente_id, "tipo": tipo, "nicho": nicho, "contenido": contenido}).execute()

def obtener_contenido():
    sb = get_client()
    res = sb.table("contenido_generado").select("*, clientes(nombre)").execute()
    contenido = []
    for c in res.data or []:
        c["cliente_nombre"] = c.get("clientes", {}).get("nombre", "Sin cliente") if c.get("clientes") else "Sin cliente"
        contenido.append(c)
    return contenido

def guardar_tendencia(titulo, descripcion, oportunidad):
    sb = get_client()
    sb.table("tendencias").insert({"titulo": titulo, "descripcion": descripcion, "oportunidad": oportunidad}).execute()

def obtener_tendencias():
    sb = get_client()
    res = sb.table("tendencias").select("*").execute()
    return res.data or []

def guardar_meta(mes, meta_ingresos, meta_clientes):
    sb = get_client()
    existing = sb.table("metas").select("id").eq("mes", mes).execute()
    if existing.data:
        sb.table("metas").update({"meta_ingresos": meta_ingresos, "meta_clientes": meta_clientes}).eq("mes", mes).execute()
    else:
        sb.table("metas").insert({"mes": mes, "meta_ingresos": meta_ingresos, "meta_clientes": meta_clientes}).execute()

def obtener_meta(mes):
    sb = get_client()
    res = sb.table("metas").select("*").eq("mes", mes).execute()
    return res.data[0] if res.data else {"meta_ingresos": 2500, "meta_clientes": 10}

def agregar_nota(cliente_id, prospecto_id, contenido):
    sb = get_client()
    sb.table("notas").insert({"cliente_id": cliente_id, "prospecto_id": prospecto_id, "contenido": contenido}).execute()

def obtener_notas(cliente_id=None, prospecto_id=None):
    sb = get_client()
    if cliente_id:
        res = sb.table("notas").select("*").eq("cliente_id", cliente_id).execute()
    elif prospecto_id:
        res = sb.table("notas").select("*").eq("prospecto_id", prospecto_id).execute()
    else:
        res = sb.table("notas").select("*").execute()
    return res.data or []

def agregar_tarea(cliente_id, titulo, fecha_vencimiento):
    sb = get_client()
    sb.table("tareas").insert({"cliente_id": cliente_id, "titulo": titulo, "fecha_vencimiento": fecha_vencimiento}).execute()

def obtener_tareas(cliente_id=None):
    sb = get_client()
    if cliente_id:
        res = sb.table("tareas").select("*").eq("cliente_id", cliente_id).execute()
    else:
        res = sb.table("tareas").select("*").execute()
    return res.data or []

def completar_tarea(tarea_id):
    sb = get_client()
    sb.table("tareas").update({"completada": True}).eq("id", tarea_id).execute()

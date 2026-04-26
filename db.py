import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    pass

def agregar_cliente(nombre, email, whatsapp, servicio, mensualidad, fecha_pago, estado, notas):
    sb = get_client()
    sb.table("clientes").insert({"nombre": nombre, "email": email, "whatsapp": whatsapp, "servicio": servicio, "mensualidad": mensualidad, "fecha_pago": fecha_pago, "estado": estado, "notas": notas}).execute()

def obtener_clientes():
    sb = get_client()
    res = sb.table("clientes").select("*").execute()
    return res.data or []

def actualizar_estado_cliente(cliente_id, nuevo_estado):
    sb = get_client()
    sb.table("clientes").update({"estado": nuevo_estado}).eq("id", cliente_id).execute()

def eliminar_cliente(cliente_id):
    sb = get_client()
    sb.table("clientes").delete().eq("id", cliente_id).execute()

def registrar_pago(cliente_id, monto, fecha, metodo, notas):
    sb = get_client()
    sb.table("pagos").insert({"cliente_id": cliente_id, "monto": monto, "fecha": fecha, "metodo": metodo, "notas": notas}).execute()

def obtener_pagos():
    sb = get_client()
    res = sb.table("pagos").select("*, clientes(nombre)").order("id", desc=True).execute()
    pagos = []
    for p in res.data or []:
        p["cliente_nombre"] = p.get("clientes", {}).get("nombre", "Sin cliente") if p.get("clientes") else "Sin cliente"
        pagos.append(p)
    return pagos

def ingresos_del_mes(mes):
    sb = get_client()
    res = sb.table("pagos").select("monto").like("fecha", f"{mes}%").execute()
    return sum(p["monto"] for p in res.data or [])

def guardar_contenido(cliente_id, tipo, nicho, contenido):
    sb = get_client()
    sb.table("contenido_generado").insert({"cliente_id": cliente_id, "tipo": tipo, "nicho": nicho, "contenido": contenido}).execute()

def obtener_contenido():
    sb = get_client()
    res = sb.table("contenido_generado").select("*, clientes(nombre)").order("id", desc=True).limit(50).execute()
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
    res = sb.table("tendencias").select("*").order("id", desc=True).limit(20).execute()
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

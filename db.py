import os
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

LAST_ERROR = None

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def _safe(fn, default=None):
    global LAST_ERROR
    try:
        result = fn()
        LAST_ERROR = None
        return result
    except Exception as e:
        LAST_ERROR = str(e)
        return default

def init_db():
    pass

def agregar_prospecto(nombre, email, whatsapp, pais, servicio_interes, presupuesto, canal, notas):
    _safe(lambda: get_client().table("prospectos").insert({"nombre": nombre, "email": email, "whatsapp": whatsapp, "pais": pais, "servicio_interes": servicio_interes, "presupuesto": presupuesto, "canal": canal, "notas": notas}).execute())

def obtener_prospectos():
    res = _safe(lambda: get_client().table("prospectos").select("*").execute())
    return res.data if res else []

def actualizar_estado_prospecto(prospecto_id, estado):
    _safe(lambda: get_client().table("prospectos").update({"estado": estado}).eq("id", prospecto_id).execute())

def actualizar_notas_prospecto(prospecto_id, notas):
    _safe(lambda: get_client().table("prospectos").update({"notas": notas}).eq("id", prospecto_id).execute())

def eliminar_prospecto(prospecto_id):
    _safe(lambda: get_client().table("prospectos").delete().eq("id", prospecto_id).execute())

def agregar_cliente(nombre, email, whatsapp, pais, servicio, mensualidad, fecha_pago, estado, notas, tipo_proyecto, monto_proyecto, pago_inicial, pago_final, estado_proyecto):
    _safe(lambda: get_client().table("clientes").insert({"nombre": nombre, "email": email, "whatsapp": whatsapp, "pais": pais, "servicio": servicio, "mensualidad": mensualidad, "fecha_pago": fecha_pago, "estado": estado, "notas": notas, "tipo_proyecto": tipo_proyecto, "monto_proyecto": monto_proyecto, "pago_inicial": pago_inicial, "pago_final": pago_final, "estado_proyecto": estado_proyecto}).execute())

def obtener_clientes():
    res = _safe(lambda: get_client().table("clientes").select("*").execute())
    return res.data if res else []

def actualizar_estado_cliente(cliente_id, nuevo_estado):
    _safe(lambda: get_client().table("clientes").update({"estado": nuevo_estado}).eq("id", cliente_id).execute())

def actualizar_estado_proyecto(cliente_id, estado_proyecto):
    _safe(lambda: get_client().table("clientes").update({"estado_proyecto": estado_proyecto}).eq("id", cliente_id).execute())

def registrar_pago_inicial(cliente_id, monto):
    _safe(lambda: get_client().table("clientes").update({"pago_inicial": monto, "estado_proyecto": "en_proceso"}).eq("id", cliente_id).execute())

def registrar_pago_final(cliente_id, monto):
    _safe(lambda: get_client().table("clientes").update({"pago_final": monto, "estado_proyecto": "entregado"}).eq("id", cliente_id).execute())

def eliminar_cliente(cliente_id):
    _safe(lambda: get_client().table("clientes").delete().eq("id", cliente_id).execute())

def registrar_pago(cliente_id, monto, fecha, metodo, notas):
    _safe(lambda: get_client().table("pagos").insert({"cliente_id": cliente_id, "monto": monto, "fecha": fecha, "metodo": metodo, "notas": notas}).execute())

def obtener_pagos():
    res = _safe(lambda: get_client().table("pagos").select("*, clientes(nombre)").execute())
    pagos = []
    for p in (res.data if res else []) or []:
        p["cliente_nombre"] = p.get("clientes", {}).get("nombre", "Sin cliente") if p.get("clientes") else "Sin cliente"
        pagos.append(p)
    return pagos

def ingresos_del_mes(mes):
    res = _safe(lambda: get_client().table("pagos").select("monto, fecha").execute())
    data = [p for p in (res.data if res else []) or [] if str(p.get("fecha", "")).startswith(mes)]
    return sum(p["monto"] for p in data)

def guardar_contenido(cliente_id, tipo, nicho, contenido):
    _safe(lambda: get_client().table("contenido_generado").insert({"cliente_id": cliente_id, "tipo": tipo, "nicho": nicho, "contenido": contenido}).execute())

def obtener_contenido():
    res = _safe(lambda: get_client().table("contenido_generado").select("*, clientes(nombre)").execute())
    contenido = []
    for c in (res.data if res else []) or []:
        c["cliente_nombre"] = c.get("clientes", {}).get("nombre", "Sin cliente") if c.get("clientes") else "Sin cliente"
        contenido.append(c)
    return contenido

def guardar_tendencia(titulo, descripcion, oportunidad):
    _safe(lambda: get_client().table("tendencias").insert({"titulo": titulo, "descripcion": descripcion, "oportunidad": oportunidad}).execute())

def obtener_tendencias():
    res = _safe(lambda: get_client().table("tendencias").select("*").execute())
    return res.data if res else []

def guardar_meta(mes, meta_ingresos, meta_clientes):
    def _do():
        sb = get_client()
        existing = sb.table("metas").select("id").eq("mes", mes).execute()
        if existing.data:
            sb.table("metas").update({"meta_ingresos": meta_ingresos, "meta_clientes": meta_clientes}).eq("mes", mes).execute()
        else:
            sb.table("metas").insert({"mes": mes, "meta_ingresos": meta_ingresos, "meta_clientes": meta_clientes}).execute()
    _safe(_do)

def obtener_meta(mes):
    default = {"meta_ingresos": 2500, "meta_clientes": 10}
    res = _safe(lambda: get_client().table("metas").select("*").eq("mes", mes).execute())
    return res.data[0] if res and res.data else default

def agregar_nota(cliente_id, prospecto_id, contenido):
    _safe(lambda: get_client().table("notas").insert({"cliente_id": cliente_id, "prospecto_id": prospecto_id, "contenido": contenido}).execute())

def obtener_notas(cliente_id=None, prospecto_id=None):
    def _do():
        sb = get_client()
        if cliente_id:
            return sb.table("notas").select("*").eq("cliente_id", cliente_id).execute()
        elif prospecto_id:
            return sb.table("notas").select("*").eq("prospecto_id", prospecto_id).execute()
        else:
            return sb.table("notas").select("*").execute()
    res = _safe(_do)
    return res.data if res else []

def agregar_tarea(cliente_id, titulo, fecha_vencimiento):
    _safe(lambda: get_client().table("tareas").insert({"cliente_id": cliente_id, "titulo": titulo, "fecha_vencimiento": fecha_vencimiento}).execute())

def obtener_tareas(cliente_id=None):
    def _do():
        sb = get_client()
        if cliente_id:
            return sb.table("tareas").select("*").eq("cliente_id", cliente_id).execute()
        else:
            return sb.table("tareas").select("*").execute()
    res = _safe(_do)
    return res.data if res else []

def completar_tarea(tarea_id):
    _safe(lambda: get_client().table("tareas").update({"completada": True}).eq("id", tarea_id).execute())

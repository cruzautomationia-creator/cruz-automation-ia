import streamlit as st
import plotly.express as px
from datetime import date, datetime
import pandas as pd
import json
import os
import re

import db
from services import ai, notifications, video, prospector

st.set_page_config(page_title="Cruz Automation IA", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
[data-testid="stSidebar"] { background: #F8F8FC; border-right: 1px solid #EEEEF8; }
div[data-testid="metric-container"] { background: white; border-radius: 14px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #EEEEF8; }
.stButton > button { border-radius: 10px; font-weight: 600; }

.stat-card { border-radius: 18px; padding: 22px 22px 18px; height: 132px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }
.stat-card .stat-label { font-size: 13px; font-weight: 600; opacity: .85; display:flex; align-items:center; gap:6px; }
.stat-card .stat-value { font-size: 30px; font-weight: 800; line-height:1.1; }
.stat-card .stat-sub { font-size: 12px; font-weight: 600; opacity: .8; }
.stat-purple { background: linear-gradient(135deg,#6C63E8,#534AB7); color: #fff; }
.stat-dark  { background: linear-gradient(135deg,#22304a,#1a2436); color: #fff; }
.stat-lime  { background: linear-gradient(135deg,#E8F27A,#D6E85C); color: #23260a; }
.stat-white { background: #ffffff; color: #23262f; border: 1px solid #EEEEF8; }

.activity-row { display:flex; align-items:center; justify-content:space-between; padding:12px 6px; border-bottom:1px solid #F0F0F7; }
.activity-row:last-child { border-bottom:none; }
.activity-left { display:flex; align-items:center; gap:12px; }
.activity-icon { width:38px; height:38px; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:17px; background:#EEEDFE; }
.activity-name { font-weight:700; font-size:14px; color:#23262f; }
.activity-sub { font-size:12px; color:#9aa2b6; }
.activity-amount { font-weight:800; font-size:14.5px; color:#23262f; }

.panel-title { font-weight:800; font-size:15.5px; color:#23262f; margin-bottom:14px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px !important; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }
div[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius:18px !important; }
</style>""", unsafe_allow_html=True)

def stat_card(clase, icono, etiqueta, valor, sub):
    st.markdown(f"""
    <div class="stat-card {clase}">
      <div class="stat-label">{icono} {etiqueta}</div>
      <div class="stat-value">{valor}</div>
      <div class="stat-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

db.init_db()

with st.sidebar:
    st.markdown("## ⚡ Cruz Automation IA")
    st.markdown("---")
    pagina = st.radio("Navegación", ["🏠 Dashboard","⭐ Prospectos","👥 Clientes","💰 Finanzas","📅 Planificación","🤖 Agentes IA","🎬 Guion de Videos","🔍 Tendencias","📧 Notificaciones","⚙️ Configuración"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<small style='color:#aaa'>Cruz Automation IA v2.0</small>", unsafe_allow_html=True)

def get_mes_actual():
    return datetime.now().strftime("%Y-%m")

def calcular_resumen():
    clientes = db.obtener_clientes()
    activos = [c for c in clientes if c["estado"] == "activo"]
    pendientes = [c for c in clientes if c["estado"] == "pendiente"]
    prospectos = db.obtener_prospectos()
    prospectos_nuevos = [p for p in prospectos if p["estado"] == "nuevo"]
    ingresos = db.ingresos_del_mes(get_mes_actual())
    pendiente_total = sum(c["mensualidad"] for c in pendientes if c.get("mensualidad"))
    return {"total_clientes": len(clientes), "activos": len(activos), "pendientes": len(pendientes), "prospectos_nuevos": len(prospectos_nuevos), "ingresos_mes": ingresos, "pendiente_cobro": pendiente_total}

if pagina == "🏠 Dashboard":
    st.title("🏠 Resumen General")
    st.markdown("Tu negocio de un vistazo")
    st.markdown("")
    resumen = calcular_resumen()
    meta = db.obtener_meta(get_mes_actual())
    progreso = (resumen["ingresos_mes"] / meta["meta_ingresos"] * 100) if meta["meta_ingresos"] > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("stat-purple", "💵", "Ingresos del mes", f"${resumen['ingresos_mes']:,.0f}", f"Meta: ${meta['meta_ingresos']:,.0f}")
    with col2:
        stat_card("stat-dark", "🎯", "Progreso de meta", f"{progreso:,.0f}%", f"${resumen['ingresos_mes']:,.0f} de ${meta['meta_ingresos']:,.0f}")
    with col3:
        stat_card("stat-lime", "👥", "Clientes activos", resumen["activos"], f"{resumen['pendientes']} pendientes de pago")
    with col4:
        stat_card("stat-white", "⭐", "Prospectos nuevos", resumen["prospectos_nuevos"], "Por convertir este mes")

    st.markdown("<br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1.1, 1])

    with col_izq:
        with st.container(border=True):
            st.markdown('<div class="panel-title">📊 Ingresos por servicio</div>', unsafe_allow_html=True)
            clientes_activos = [c for c in db.obtener_clientes() if c["estado"] == "activo" and c.get("mensualidad")]
            if clientes_activos:
                df_serv = pd.DataFrame(clientes_activos).groupby("servicio")["mensualidad"].sum().reset_index()
                fig = px.pie(df_serv, names="servicio", values="mensualidad", hole=0.62,
                             color_discrete_sequence=["#534AB7", "#8F87E0", "#D6E85C", "#22304a", "#B8B2F2"])
                fig.update_traces(textinfo="percent", textfont_size=12)
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.25),
                                   margin=dict(t=10, b=10, l=10, r=10), height=300,
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Agrega clientes activos con mensualidad para ver el desglose.")

    with col_der:
        with st.container(border=True):
            st.markdown('<div class="panel-title">🕒 Actividad reciente</div>', unsafe_allow_html=True)
            pagos = db.obtener_pagos()
            if pagos:
                pagos_ordenados = sorted(pagos, key=lambda p: p.get("fecha", ""), reverse=True)[:6]
                iconos = {"transferencia": "🏦", "efectivo": "💵", "paypal": "🅿️", "tarjeta": "💳"}
                filas = "".join(f"""
                <div class="activity-row">
                  <div class="activity-left">
                    <div class="activity-icon">{iconos.get(str(p.get('metodo','')).lower(), '💰')}</div>
                    <div>
                      <div class="activity-name">{p.get('cliente_nombre','Sin cliente')}</div>
                      <div class="activity-sub">{p.get('fecha','')}</div>
                    </div>
                  </div>
                  <div class="activity-amount">${p.get('monto',0):,.0f}</div>
                </div>""" for p in pagos_ordenados)
                st.markdown(filas, unsafe_allow_html=True)
            else:
                st.info("Registra pagos para ver la actividad reciente aquí.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="panel-title">🤖 Agentes IA</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**💜 Agente Financiero**\nAnaliza ingresos y sugiere estrategias")
            st.info("**🟠 Agente de Precios**\nCotiza proyectos con tus precios reales")
        with col2:
            st.info("**🟢 Agente de Tendencias**\nBusca oportunidades en internet hoy")
            st.info("**📄 Agente de Propuestas**\nGenera propuestas con tu marca")
        with col3:
            st.info("**📝 Agente de Acuerdos**\nAcuerdos de servicio profesionales")
            st.info("**🔴 Agente de Cobros**\nMensajes de cobro para WhatsApp")

    st.markdown("<br>", unsafe_allow_html=True)
    pagos_todos = db.obtener_pagos()
    if pagos_todos:
        with st.container(border=True):
            st.markdown('<div class="panel-title">📈 Ingresos por mes</div>', unsafe_allow_html=True)
            df = pd.DataFrame(pagos_todos)
            df["fecha"] = pd.to_datetime(df["fecha"])
            df_mes = df.groupby(df["fecha"].dt.strftime("%Y-%m"))["monto"].sum().reset_index()
            df_mes.columns = ["Mes", "Ingresos"]
            fig = px.bar(df_mes, x="Mes", y="Ingresos", color_discrete_sequence=["#534AB7"])
            fig.update_traces(marker_cornerradius=8)
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Agrega clientes y registra pagos para ver el gráfico.")

elif pagina == "⭐ Prospectos":
    st.title("⭐ Prospectos")

    pendientes = prospector.pendientes_reales()
    if pendientes:
        st.warning(f"🤖 El agente encontró **{len(pendientes)} negocios nuevos** hoy en la madrugada, esperando que los proceses.")
        if st.button("⚡ Procesar todos ahora (redactar, guardar y enviar emails)", type="primary"):
            with st.spinner(f"Procesando {len(pendientes)} leads..."):
                try:
                    resultados = prospector.procesar_pendientes()
                    ok = sum(1 for r in resultados if not r.get("omitido"))
                    try:
                        prospector.revisar_respuestas()
                    except Exception:
                        pass
                    st.success(f"✅ Listo: {ok} negocios procesados y guardados en Prospectos. También revisé respuestas nuevas de leads anteriores.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")
        with st.expander("Ver lista sin procesar"):
            for p in pendientes:
                st.write(f"**{p['nombre']}** — {p['pais']} — {p['debilidad']}")

    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Ver prospectos", "➕ Agregar prospecto"])
    with tab1:
        prospectos = db.obtener_prospectos()
        if not prospectos:
            st.info("No hay prospectos aún.")
        else:
            with st.expander("🗑️ Eliminar todos los prospectos"):
                st.warning("Esto borra TODOS los prospectos de forma permanente. No se puede deshacer.")
                confirmar_borrar_todo = st.checkbox("Sí, quiero borrar todos los prospectos", key="confirmar_borrar_todo")
                if st.button("Eliminar todos ahora", disabled=not confirmar_borrar_todo, key="btn_borrar_todo"):
                    for p in prospectos:
                        db.eliminar_prospecto(p["id"])
                    st.success("Todos los prospectos fueron eliminados.")
                    st.rerun()
            for p in prospectos:
                if p["estado"] in ["descartado","convertido"]:
                    continue
                with st.expander(f"{'🔵' if p['estado']=='nuevo' else '🟡'} {p['nombre']} — {p['servicio_interes']} — {p.get('pais','')} — {p['canal']}"):
                    notas_raw = p.get("notas") or ""
                    link_whatsapp = None
                    match_link = re.search(r"WHATSAPP_LINK::(\S+)", notas_raw)
                    if match_link:
                        link_whatsapp = match_link.group(1)
                    notas_visibles = re.sub(r"\n*WHATSAPP_LINK::\S+\n*", "\n", notas_raw).strip()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"📧 {p['email'] or 'Sin email'}")
                        st.write(f"📱 {p['whatsapp'] or 'Sin WhatsApp'}")
                        st.write(f"💰 Presupuesto: {p['presupuesto'] or 'No indicado'}")
                    with col2:
                        st.write(f"📅 Llegó: {p['fecha'][:10]}")
                    if link_whatsapp:
                        if "[WhatsApp enviado" in notas_visibles:
                            st.success("📱 WhatsApp ya enviado — esperando respuesta")
                            st.link_button("Reabrir conversación de WhatsApp", link_whatsapp)
                        else:
                            if st.button("📱 Enviar por WhatsApp (1 clic)", key=f"wa_{p['id']}", type="primary"):
                                db.actualizar_notas_prospecto(p["id"], notas_raw + "\n\n[WhatsApp enviado, esperando respuesta]")
                                st.markdown(f"<script>window.open('{link_whatsapp}','_blank')</script>", unsafe_allow_html=True)
                                st.success("✅ Marcado como enviado. Se abrió WhatsApp en una pestaña nueva.")
                                st.rerun()
                    if notas_visibles:
                        st.info(notas_visibles)
                        nuevo_estado = st.selectbox("Estado", ["nuevo","en_negociacion","convertido","descartado"], key=f"est_{p['id']}", index=["nuevo","en_negociacion","convertido","descartado"].index(p["estado"]))
                        if st.button("Actualizar", key=f"upd_{p['id']}"):
                            db.actualizar_estado_prospecto(p["id"], nuevo_estado)
                            st.rerun()
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("📄 Generar propuesta", key=f"prop_{p['id']}"):
                            with st.spinner("Generando..."):
                                try:
                                    propuesta = ai.generar_propuesta(p["nombre"], p.get("pais",""), p["servicio_interes"], p.get("presupuesto",""), p.get("notas",""))
                                    st.markdown(f"**{propuesta.get('asunto','')}**")
                                    st.write(propuesta.get("introduccion",""))
                                    st.write(propuesta.get("propuesta_servicio",""))
                                    st.markdown(f"**Precio:** {propuesta.get('precio','')}")
                                    st.markdown(f"**Entrega:** {propuesta.get('tiempo_entrega','')}")
                                    st.markdown(f"**Pago:** {propuesta.get('forma_pago','')}")
                                except Exception as ex:
                                    st.error(f"Error: {ex}")
                    with col2:
                        if st.button("📝 Generar acuerdo", key=f"acrd_{p['id']}"):
                            with st.spinner("Generando..."):
                                try:
                                    acuerdo = ai.generar_acuerdo(p["nombre"], p.get("email",""), p.get("pais",""), p["servicio_interes"], p.get("presupuesto","0"), p["servicio_interes"], str(date.today()))
                                    for key, val in acuerdo.items():
                                        if isinstance(val, list):
                                            st.markdown(f"**{key}:**")
                                            for item in val:
                                                st.markdown(f"- {item}")
                                        else:
                                            st.markdown(f"**{key}:** {val}")
                                except Exception as ex:
                                    st.error(f"Error: {ex}")
                    with col3:
                        if st.button("✅ Convertir", key=f"conv_{p['id']}"):
                            db.actualizar_estado_prospecto(p["id"], "convertido")
                            st.success("Convertido. Ve a Clientes.")
                            st.rerun()
                    with col4:
                        if st.button("🗑️ Eliminar", key=f"del_p_{p['id']}"):
                            db.eliminar_prospecto(p["id"])
                            st.rerun()
                    nueva_nota = st.text_input("Agregar nota", key=f"nota_p_{p['id']}")
                    if st.button("💾 Guardar nota", key=f"savnota_p_{p['id']}"):
                        if nueva_nota:
                            db.agregar_nota(None, p["id"], nueva_nota)
                            st.rerun()
    with tab2:
        with st.form("form_prospecto"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                email = st.text_input("Email")
                whatsapp = st.text_input("WhatsApp")
                pais = st.text_input("País")
            with col2:
                servicio_interes = st.selectbox("Servicio", ["Sitio web","Landing page","E-commerce","Portafolio","Automatización WhatsApp","Automatización Instagram","Automatización TikTok","Combo completo","Otro"])
                presupuesto = st.text_input("Presupuesto")
                canal = st.selectbox("Canal", ["Manual","Sitio web","WhatsApp","Instagram","TikTok","Referido","Otro"])
            notas = st.text_area("Notas")
            if st.form_submit_button("✅ Guardar"):
                if nombre:
                    db.agregar_prospecto(nombre, email, whatsapp, pais, servicio_interes, presupuesto, canal, notas)
                    st.success(f"✅ {nombre} agregado.")
                else:
                    st.error("El nombre es obligatorio.")

elif pagina == "👥 Clientes":
    st.title("👥 CRM de Clientes")
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📋 Ver clientes", "➕ Agregar cliente", "💳 Registrar pago"])
    with tab1:
        clientes = db.obtener_clientes()
        if not clientes:
            st.info("Aún no tienes clientes.")
        else:
            for c in clientes:
                with st.expander(f"{'🟢' if c['estado']=='activo' else '🟡'} {c['nombre']} — {c['servicio']} — ${c.get('mensualidad',0)}/mes"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"📧 {c['email'] or 'Sin email'}")
                        st.write(f"📱 {c['whatsapp'] or 'Sin WhatsApp'}")
                        st.write(f"🌍 {c.get('pais','Sin país')}")
                    with col2:
                        st.write(f"📅 Próximo pago: {c['fecha_pago'] or 'No definido'}")
                        st.write(f"🏗️ Proyecto: {c.get('estado_proyecto','pendiente')}")
                        st.write(f"💰 Monto proyecto: ${c.get('monto_proyecto',0)}")
                    with col3:
                        nuevo_estado = "pendiente" if c["estado"] == "activo" else "activo"
                        if st.button(f"Cambiar a {nuevo_estado}", key=f"est_c_{c['id']}"):
                            db.actualizar_estado_cliente(c["id"], nuevo_estado)
                            st.rerun()
                        if c.get("estado_proyecto") == "en_proceso":
                            if st.button("✅ Marcar entregado", key=f"entr_c_{c['id']}"):
                                db.actualizar_estado_proyecto(c["id"], "entregado")
                                st.rerun()
                        if st.button("🗑️ Eliminar", key=f"del_c_{c['id']}"):
                            db.eliminar_cliente(c["id"])
                            st.rerun()
                    notas = db.obtener_notas(cliente_id=c["id"])
                    if notas:
                        st.markdown("**📋 Notas:**")
                        for nota in notas:
                            st.markdown(f"- {nota['fecha'][:10]}: {nota['contenido']}")
                    nueva_nota = st.text_input("Agregar nota", key=f"nota_c_{c['id']}")
                    if st.button("💾 Guardar nota", key=f"savnota_c_{c['id']}"):
                        if nueva_nota:
                            db.agregar_nota(c["id"], None, nueva_nota)
                            st.rerun()
    with tab2:
        with st.form("form_cliente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                email = st.text_input("Email")
                whatsapp = st.text_input("WhatsApp")
                pais = st.text_input("País")
            with col2:
                servicio = st.selectbox("Servicio", ["Sitio web","Landing page","E-commerce","Portafolio","Automatización WhatsApp","Automatización Instagram","Automatización TikTok","Combo completo","Gestión de contenido","Otro"])
                mensualidad = st.number_input("Mensualidad ($)", min_value=0.0, value=80.0)
                fecha_pago = st.date_input("Próxima fecha de pago", value=date.today())
                estado = st.selectbox("Estado", ["activo","pendiente"])
            st.markdown("**Proyecto:**")
            col1, col2 = st.columns(2)
            with col1:
                tipo_proyecto = st.selectbox("Tipo", ["proyecto_unico","mensualidad","combo"])
                monto_proyecto = st.number_input("Monto total ($)", min_value=0.0, value=0.0)
            with col2:
                pago_inicial = st.number_input("Pago inicial ($)", min_value=0.0, value=0.0)
                estado_proyecto = st.selectbox("Estado proyecto", ["pendiente","en_proceso","entregado"])
            notas = st.text_area("Notas")
            if st.form_submit_button("✅ Guardar cliente"):
                if nombre:
                    db.agregar_cliente(nombre, email, whatsapp, pais, servicio, mensualidad, str(fecha_pago), estado, notas, tipo_proyecto, monto_proyecto, pago_inicial, 0, estado_proyecto)
                    if email:
                        notifications.email_bienvenida(nombre, email, servicio, mensualidad)
                    st.success(f"✅ {nombre} agregado.")
                else:
                    st.error("El nombre es obligatorio.")
    with tab3:
        clientes = db.obtener_clientes()
        if not clientes:
            st.info("Primero agrega un cliente.")
        else:
            with st.form("form_pago"):
                opciones = {c["nombre"]: c["id"] for c in clientes}
                cliente_sel = st.selectbox("Cliente", list(opciones.keys()))
                cliente_data = next(c for c in clientes if c["nombre"] == cliente_sel)
                tipo_pago = st.selectbox("Tipo", ["Mensualidad","50% inicial","50% final","Pago completo","Otro"])
                monto = st.number_input("Monto ($)", value=float(cliente_data.get("mensualidad",0) or 0))
                fecha = st.date_input("Fecha", value=date.today())
                metodo = st.selectbox("Método", ["Transferencia","Efectivo","PayPal","Otro"])
                notas_pago = st.text_input("Notas")
                if st.form_submit_button("💾 Registrar"):
                    db.registrar_pago(opciones[cliente_sel], monto, str(fecha), metodo, f"{tipo_pago} - {notas_pago}")
                    if "inicial" in tipo_pago.lower():
                        db.registrar_pago_inicial(opciones[cliente_sel], monto)
                    elif "final" in tipo_pago.lower():
                        db.registrar_pago_final(opciones[cliente_sel], monto)
                    db.actualizar_estado_cliente(opciones[cliente_sel], "activo")
                    st.success(f"✅ ${monto} registrado.")

elif pagina == "💰 Finanzas":
    st.title("💰 Panel Financiero")
    st.markdown("---")
    resumen = calcular_resumen()
    meta = db.obtener_meta(get_mes_actual())
    clientes = db.obtener_clientes()
    mensualidades_activas = sum(c.get("mensualidad",0) or 0 for c in clientes if c["estado"] == "activo")
    proyectos_pendientes = sum((c.get("monto_proyecto",0) or 0) - (c.get("pago_inicial",0) or 0) - (c.get("pago_final",0) or 0) for c in clientes if c.get("estado_proyecto") == "en_proceso")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Ingresos del mes", f"${resumen['ingresos_mes']:,.0f}")
    with col2:
        st.metric("🔧 Mensualidades", f"${mensualidades_activas:,.0f}/mes")
    with col3:
        st.metric("🏗️ Proyectos por cobrar", f"${max(0,proyectos_pendientes):,.0f}")
    with col4:
        faltan = max(0, meta["meta_ingresos"] - resumen["ingresos_mes"])
        st.metric("🎯 Para meta", f"${faltan:,.0f}")
    progreso_val = min(1.0, resumen["ingresos_mes"] / meta["meta_ingresos"]) if meta["meta_ingresos"] > 0 else 0
    st.progress(progreso_val, text=f"Meta: {progreso_val*100:.0f}% — ${resumen['ingresos_mes']:,.0f} de ${meta['meta_ingresos']:,.0f}")
    st.markdown("---")
    with st.expander("⚙️ Configurar meta"):
        with st.form("form_meta"):
            nueva_meta = st.number_input("Meta ($)", value=float(meta["meta_ingresos"]))
            meta_clientes = st.number_input("Meta clientes", value=int(meta.get("meta_clientes",10)))
            if st.form_submit_button("Guardar"):
                db.guardar_meta(get_mes_actual(), nueva_meta, meta_clientes)
                st.success("✅ Meta guardada.")
                st.rerun()
    if st.button("🤖 Analizar finanzas con IA", type="primary"):
        servicios = list(set(c["servicio"] for c in clientes)) if clientes else ["varios"]
        with st.spinner("Analizando..."):
            try:
                analisis = ai.analizar_finanzas(resumen["ingresos_mes"], resumen["pendiente_cobro"], meta["meta_ingresos"], resumen["activos"], ", ".join(servicios))
                st.success("✅ Análisis completado")
                st.markdown(f"**Diagnóstico:** {analisis.get('diagnostico','')}")
                st.markdown(f"**Acción hoy:** {analisis.get('accion_hoy','')}")
                for e in analisis.get("estrategias",[]):
                    st.markdown(f"- {e}")
            except Exception as ex:
                st.error(f"Error: {ex}")
    pagos = db.obtener_pagos()
    if pagos:
        st.markdown("---")
        df = pd.DataFrame(pagos)[["cliente_nombre","monto","fecha","metodo","notas"]]
        df.columns = ["Cliente","Monto","Fecha","Método","Notas"]
        st.dataframe(df, use_container_width=True)

elif pagina == "📅 Planificación":
    st.title("📅 Planificación de Contenido")
    st.markdown("---")
    clientes = db.obtener_clientes()
    if not clientes:
        st.info("Primero agrega clientes.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            opciones = {c["nombre"]: c for c in clientes}
            cliente_sel = st.selectbox("Cliente", list(opciones.keys()))
            cliente_data = opciones[cliente_sel]
        with col2:
            mes = st.selectbox("Mes", ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        if st.button("🤖 Generar plan con IA", type="primary"):
            with st.spinner("Generando..."):
                try:
                    plan = ai.generar_plan_contenido(cliente_sel, cliente_data["servicio"], mes)
                    st.success("✅ Plan generado")
                    for semana, posts in plan.items():
                        if semana.startswith("semana") and isinstance(posts, list):
                            st.subheader(f"Semana {semana.split('_')[1]}")
                            st.dataframe(pd.DataFrame(posts), use_container_width=True)
                    if plan.get("estrategia_general"):
                        st.info(f"**Estrategia:** {plan['estrategia_general']}")
                    db.guardar_contenido(cliente_data["id"], "plan_mensual", cliente_data["servicio"], json.dumps(plan, ensure_ascii=False))
                except Exception as ex:
                    st.error(f"Error: {ex}")

elif pagina == "🤖 Agentes IA":
    st.title("🤖 Centro de Agentes IA")
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💰 Cotizador", "📄 Propuesta", "📝 Acuerdo"])
    with tab1:
        st.subheader("Agente de Precios")
        col1, col2 = st.columns(2)
        with col1:
            nombre_cot = st.text_input("Nombre del cliente", key="cot_nombre")
            pais_cot = st.text_input("País", key="cot_pais")
        with col2:
            descripcion = st.text_area("Describe el proyecto", key="cot_desc")
        if st.button("💰 Cotizar", type="primary"):
            if descripcion:
                with st.spinner("Calculando..."):
                    try:
                        cot = ai.generar_cotizacion(descripcion, nombre_cot or "Cliente", pais_cot or "Latam")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Precio total", f"${cot.get('precio_total',0)} USD")
                        with col2:
                            st.metric("Entrega", cot.get("tiempo_entrega",""))
                        if cot.get("nombre_combo_o_detalle"):
                            st.markdown(f"**{cot.get('nombre_combo_o_detalle')}**")
                        st.markdown("**Detalle:**")
                        for s in cot.get("servicios_elegidos",[]):
                            st.markdown(f"- {s.get('categoria','')}: {s.get('opcion','')} — ${s.get('precio',0)} USD")
                        st.markdown("**Incluye:**")
                        for item in cot.get("incluye",[]):
                            st.markdown(f"- {item}")
                        st.info(cot.get("justificacion",""))
                        with st.expander("Ver alternativas"):
                            st.write(f"💸 Más económica: {cot.get('alternativa_economica','')}")
                            st.write(f"✨ Premium: {cot.get('alternativa_premium','')}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")
    with tab2:
        st.subheader("Agente de Propuestas")
        prospectos = db.obtener_prospectos()
        activos = [p for p in prospectos if p["estado"] not in ["convertido","descartado"]]
        if activos:
            opciones_p = {p["nombre"]: p for p in activos}
            sel = st.selectbox("Prospecto", list(opciones_p.keys()))
            p = opciones_p[sel]
            if st.button("📄 Generar propuesta", type="primary"):
                with st.spinner("Generando..."):
                    try:
                        prop = ai.generar_propuesta(p["nombre"], p.get("pais",""), p["servicio_interes"], p.get("presupuesto",""), p.get("notas",""))
                        st.markdown(f"### {prop.get('asunto','')}")
                        st.write(prop.get("introduccion",""))
                        st.write(prop.get("propuesta_servicio",""))
                        st.markdown(f"**Precio:** {prop.get('precio','')}")
                        for item in prop.get("incluye",[]):
                            st.markdown(f"- {item}")
                        st.markdown(f"**Entrega:** {prop.get('tiempo_entrega','')}")
                        st.markdown(f"**Pago:** {prop.get('forma_pago','')}")
                        st.write(prop.get("cierre",""))
                    except Exception as ex:
                        st.error(f"Error: {ex}")
        else:
            st.info("No hay prospectos activos.")
    with tab3:
        st.subheader("Agente de Acuerdos")
        col1, col2 = st.columns(2)
        with col1:
            nombre_ac = st.text_input("Nombre del cliente", key="ac_nombre")
            email_ac = st.text_input("Email", key="ac_email")
            pais_ac = st.text_input("País", key="ac_pais")
        with col2:
            servicio_ac = st.text_input("Servicio acordado", key="ac_servicio")
            monto_ac = st.number_input("Monto total ($)", min_value=0.0, value=120.0, key="ac_monto")
            fecha_ac = st.date_input("Fecha inicio", value=date.today(), key="ac_fecha")
        incluye_ac = st.text_area("¿Qué incluye?", key="ac_incluye")
        if st.button("📝 Generar acuerdo", type="primary"):
            if nombre_ac and servicio_ac:
                with st.spinner("Generando..."):
                    try:
                        acuerdo = ai.generar_acuerdo(nombre_ac, email_ac, pais_ac, servicio_ac, monto_ac, incluye_ac, str(fecha_ac))
                        st.markdown(f"# {acuerdo.get('titulo','ACUERDO DE SERVICIO')}")
                        for key, val in acuerdo.items():
                            if key == "titulo":
                                continue
                            if isinstance(val, list):
                                st.markdown(f"**{key.upper()}:**")
                                for item in val:
                                    st.markdown(f"- {item}")
                            else:
                                st.markdown(f"**{key.upper()}:** {val}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

elif pagina == "🎬 Guion de Videos":
    st.title("🎬 Extractor de Guion de Videos")
    st.markdown("Extrae la transcripción completa de un video: pega un link o sube el archivo descargado.")
    st.markdown("---")
    tab1, tab2 = st.tabs(["🔗 Desde un link", "📁 Subir video descargado"])
    with tab1:
        url = st.text_input("Link del video (YouTube, TikTok, Instagram)", key="video_url")
        if st.button("🎬 Extraer guion", type="primary", key="btn_url"):
            if url:
                with st.spinner("Extrayendo guion..."):
                    try:
                        guion, origen = video.extraer_guion_url(url)
                        st.success("✅ Guion extraído" + (" (subtítulos originales)" if origen == "captions" else " (transcrito con IA)"))
                        st.text_area("Guion completo", guion, height=400, key="guion_url")
                        st.download_button("⬇️ Descargar .txt", guion, file_name="guion.txt", key="dl_url")
                    except Exception as ex:
                        st.error(f"Error: {ex}")
            else:
                st.warning("Pega un link primero.")
    with tab2:
        archivo = st.file_uploader("Video o audio descargado", type=["mp4","mov","mkv","webm","mp3","wav","m4a"], key="video_file")
        if archivo and st.button("🎬 Extraer guion", type="primary", key="btn_file"):
            with st.spinner("Transcribiendo..."):
                try:
                    guion = video.extraer_guion_archivo(archivo)
                    st.success("✅ Guion extraído")
                    st.text_area("Guion completo", guion, height=400, key="guion_file")
                    st.download_button("⬇️ Descargar .txt", guion, file_name="guion.txt", key="dl_file")
                except Exception as ex:
                    st.error(f"Error: {ex}")

elif pagina == "🔍 Tendencias":
    st.title("🔍 Agente de Tendencias")
    st.markdown("---")
    if st.button("🔄 Investigar tendencias", type="primary"):
        with st.spinner("Investigando..."):
            try:
                resultado = ai.investigar_tendencias()
                for t in resultado.get("tendencias",[]):
                    db.guardar_tendencia(t["titulo"], t["descripcion"], t.get("accion_concreta", t["oportunidad"]))
                st.success("✅ Tendencias actualizadas")
                st.info(resultado.get("resumen",""))
                st.warning(resultado.get("accion_inmediata",""))
            except Exception as ex:
                st.error(f"Error: {ex}")
    tendencias = db.obtener_tendencias()
    if tendencias:
        for t in tendencias:
            with st.expander(f"💡 {t['titulo']}"):
                st.write(t["descripcion"])
                st.success(t["oportunidad"])
                st.caption(t["fecha"][:10])
    else:
        st.info("Haz click para investigar tendencias.")

elif pagina == "📧 Notificaciones":
    st.title("📧 Notificaciones y Cobros")
    st.markdown("---")
    clientes = db.obtener_clientes()
    pendientes = [c for c in clientes if c["estado"] == "pendiente"]
    proyectos_cobrar = [c for c in clientes if c.get("estado_proyecto") == "en_proceso" and (c.get("monto_proyecto",0) or 0) > ((c.get("pago_inicial",0) or 0) + (c.get("pago_final",0) or 0))]
    prospectos = db.obtener_prospectos()
    sin_responder = [p for p in prospectos if p["estado"] == "nuevo"]
    if sin_responder:
        st.warning(f"⭐ {len(sin_responder)} prospectos sin responder")
    st.subheader(f"⚠️ Mensualidades pendientes ({len(pendientes)})")
    if not pendientes:
        st.success("✅ No hay pendientes.")
    for c in pendientes:
        with st.expander(f"{c['nombre']} — ${c.get('mensualidad',0)}/mes"):
            col1, col2 = st.columns(2)
            with col1:
                if c["email"] and st.button("📧 Email", key=f"rec_n_{c['id']}"):
                    ok, msg = notifications.email_recordatorio_pago(c["nombre"], c["email"], c.get("mensualidad",0), c["servicio"], c["fecha_pago"] or "fecha acordada")
                    st.success("Enviado") if ok else st.error(msg)
            with col2:
                if st.button("🤖 Mensaje WhatsApp", key=f"wa_n_{c['id']}"):
                    with st.spinner("..."):
                        try:
                            msg = ai.generar_mensaje_cobro(c["nombre"], c.get("mensualidad",0), c["servicio"])
                            st.text_area("Copia:", msg, key=f"msg_n_{c['id']}")
                        except Exception as ex:
                            st.error(f"Error: {ex}")
    if proyectos_cobrar:
        st.subheader(f"🏗️ Proyectos por cobrar ({len(proyectos_cobrar)})")
        for c in proyectos_cobrar:
            pendiente = (c.get("monto_proyecto",0) or 0) - (c.get("pago_inicial",0) or 0) - (c.get("pago_final",0) or 0)
            with st.expander(f"{c['nombre']} — ${pendiente} pendiente"):
                if st.button("🤖 Mensaje cobro final", key=f"fin_n_{c['id']}"):
                    with st.spinner("..."):
                        try:
                            msg = ai.generar_mensaje_cobro(c["nombre"], pendiente, c["servicio"], "pago final")
                            st.text_area("Copia:", msg, key=f"msgfin_n_{c['id']}")
                        except Exception as ex:
                            st.error(f"Error: {ex}")

elif pagina == "⚙️ Configuración":
    st.title("⚙️ Configuración")
    st.markdown("---")
    clientes = db.obtener_clientes()
    prospectos = db.obtener_prospectos()
    pagos = db.obtener_pagos()
    col1, col2, col3 = st.columns(3)
    col1.metric("Clientes", len(clientes))
    col2.metric("Prospectos", len(prospectos))
    col3.metric("Pagos", len(pagos))
    st.markdown("---")
    st.info("Cruz Automation IA v2.0")

if db.LAST_ERROR:
    with st.sidebar:
        st.warning(f"⚠️ Sin conexión a la base de datos.\n\n{db.LAST_ERROR}")

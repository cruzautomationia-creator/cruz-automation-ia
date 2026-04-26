import streamlit as st
import plotly.express as px
from datetime import date, datetime
import pandas as pd
import json
import os

import db
from services import ai, notifications

st.set_page_config(
    page_title="Cruz Automation IA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #FAFAFA; }
    h1, h2, h3 { color: #1A1A2E !important; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

db.init_db()

with st.sidebar:
    st.markdown("## ⚡ Cruz Automation IA")
    st.markdown("---")
    pagina = st.radio("Navegación", [
        "🏠 Dashboard",
        "👥 Clientes",
        "💰 Finanzas",
        "📅 Planificación",
        "🔍 Tendencias",
        "📧 Notificaciones",
        "⚙️ Configuración"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<small style='color:#aaa'>Cruz Automation IA v1.0</small>", unsafe_allow_html=True)

def get_mes_actual():
    return datetime.now().strftime("%Y-%m")

def calcular_resumen():
    clientes = db.obtener_clientes()
    activos = [c for c in clientes if c["estado"] == "activo"]
    pendientes = [c for c in clientes if c["estado"] == "pendiente"]
    ingresos = db.ingresos_del_mes(get_mes_actual())
    pendiente_total = sum(c["mensualidad"] for c in pendientes)
    return {
        "total_clientes": len(clientes),
        "activos": len(activos),
        "pendientes": len(pendientes),
        "ingresos_mes": ingresos,
        "pendiente_cobro": pendiente_total
    }

if pagina == "🏠 Dashboard":
    st.title("🏠 Resumen General")
    st.markdown("Tu negocio de un vistazo")
    st.markdown("---")
    resumen = calcular_resumen()
    meta = db.obtener_meta(get_mes_actual())
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Ingresos del mes", f"${resumen['ingresos_mes']:,.0f}", delta=f"Meta: ${meta['meta_ingresos']:,.0f}")
    with col2:
        st.metric("👥 Clientes activos", resumen["activos"])
    with col3:
        st.metric("⚠️ Cobros pendientes", f"${resumen['pendiente_cobro']:,.0f}", delta=f"{resumen['pendientes']} clientes", delta_color="inverse")
    with col4:
        progreso = (resumen["ingresos_mes"] / meta["meta_ingresos"] * 100) if meta["meta_ingresos"] > 0 else 0
        st.metric("🎯 Progreso meta", f"{progreso:.0f}%")
    st.markdown("---")
    st.subheader("🤖 Agentes IA")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### 💜 Agente Financiero")
            st.caption("Analiza ingresos y te dice cómo llegar a tu meta")
        with st.container(border=True):
            st.markdown("#### 📅 Planificación de contenido")
            st.caption("Organiza el contenido mensual de cada cliente")
    with col2:
        with st.container(border=True):
            st.markdown("#### 🟢 Agente de Tendencias")
            st.caption("Detecta oportunidades en tu nicho cada día")
        with st.container(border=True):
            st.markdown("#### 🔴 Agente de Cobros")
            st.caption("Detecta morosos y envía recordatorios")
    st.markdown("---")
    st.subheader("📈 Ingresos recientes")
    pagos = db.obtener_pagos()
    if pagos:
        df = pd.DataFrame(pagos)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df_mes = df.groupby(df["fecha"].dt.strftime("%Y-%m"))["monto"].sum().reset_index()
        df_mes.columns = ["Mes", "Ingresos"]
        fig = px.bar(df_mes, x="Mes", y="Ingresos", color_discrete_sequence=["#534AB7"])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Agrega clientes y registra pagos para ver el gráfico.")

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
                with st.expander(f"{'🟢' if c['estado']=='activo' else '🟡'} {c['nombre']} — {c['servicio']} — ${c['mensualidad']}/mes"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"📧 {c['email'] or 'Sin email'}")
                        st.write(f"📱 {c['whatsapp'] or 'Sin WhatsApp'}")
                    with col2:
                        st.write(f"📅 Próximo pago: {c['fecha_pago'] or 'No definido'}")
                        st.write(f"📝 {c['notas'] or 'Sin notas'}")
                    with col3:
                        nuevo_estado = "pendiente" if c["estado"] == "activo" else "activo"
                        if st.button(f"Cambiar a {nuevo_estado}", key=f"estado_{c['id']}"):
                            db.actualizar_estado_cliente(c["id"], nuevo_estado)
                            st.rerun()
                        if st.button("🗑️ Eliminar", key=f"del_{c['id']}"):
                            db.eliminar_cliente(c["id"])
                            st.rerun()
    with tab2:
        with st.form("form_cliente"):
            st.subheader("Nuevo cliente")
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo *")
                email = st.text_input("Email")
                whatsapp = st.text_input("WhatsApp")
            with col2:
                servicio = st.selectbox("Servicio", ["Sitio web", "Portafolio / Marca personal", "Automatización WhatsApp", "Automatización Instagram", "Automatización TikTok", "Carruseles mensuales", "Gestión de contenido", "Paquete completo", "Otro"])
                mensualidad = st.number_input("Mensualidad ($)", min_value=0.0, value=150.0)
                fecha_pago = st.date_input("Próxima fecha de pago", value=date.today())
                estado = st.selectbox("Estado", ["activo", "pendiente"])
            notas = st.text_area("Notas")
            if st.form_submit_button("✅ Guardar cliente"):
                if nombre:
                    db.agregar_cliente(nombre, email, whatsapp, servicio, mensualidad, str(fecha_pago), estado, notas)
                    if email:
                        notifications.email_bienvenida(nombre, email, servicio, mensualidad)
                    st.success(f"✅ Cliente '{nombre}' agregado.")
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
                monto = st.number_input("Monto ($)", value=float(cliente_data["mensualidad"]))
                fecha = st.date_input("Fecha del pago", value=date.today())
                metodo = st.selectbox("Método", ["Transferencia", "Efectivo", "PayPal", "Otro"])
                notas_pago = st.text_input("Notas")
                if st.form_submit_button("💾 Registrar pago"):
                    db.registrar_pago(opciones[cliente_sel], monto, str(fecha), metodo, notas_pago)
                    db.actualizar_estado_cliente(opciones[cliente_sel], "activo")
                    st.success(f"✅ Pago de ${monto} registrado.")

elif pagina == "💰 Finanzas":
    st.title("💰 Panel Financiero")
    st.markdown("---")
    resumen = calcular_resumen()
    meta = db.obtener_meta(get_mes_actual())
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ingresos confirmados", f"${resumen['ingresos_mes']:,.0f}")
    with col2:
        st.metric("Por cobrar", f"${resumen['pendiente_cobro']:,.0f}")
    with col3:
        faltan = max(0, meta["meta_ingresos"] - resumen["ingresos_mes"] - resumen["pendiente_cobro"])
        st.metric("Para llegar a meta", f"${faltan:,.0f}")
    progreso = min(100, (resumen["ingresos_mes"] / meta["meta_ingresos"] * 100)) if meta["meta_ingresos"] > 0 else 0
    st.progress(progreso / 100, text=f"Meta: {progreso:.0f}% — ${resumen['ingresos_mes']:,.0f} de ${meta['meta_ingresos']:,.0f}")
    st.markdown("---")
    with st.expander("⚙️ Configurar meta mensual"):
        with st.form("form_meta"):
            nueva_meta = st.number_input("Meta de ingresos ($)", value=float(meta["meta_ingresos"]))
            meta_clientes = st.number_input("Meta de clientes", value=int(meta.get("meta_clientes", 10)))
            if st.form_submit_button("Guardar meta"):
                db.guardar_meta(get_mes_actual(), nueva_meta, meta_clientes)
                st.success("Meta guardada.")
                st.rerun()
    st.subheader("🤖 Análisis del Agente Financiero")
    if st.button("Analizar mis finanzas con IA"):
        clientes = db.obtener_clientes()
        servicios = list(set(c["servicio"] for c in clientes)) if clientes else ["varios"]
        with st.spinner("Analizando..."):
            try:
                analisis = ai.analizar_finanzas(resumen["ingresos_mes"], resumen["pendiente_cobro"], meta["meta_ingresos"], resumen["activos"], ", ".join(servicios))
                st.success("✅ Análisis completado")
                st.markdown(f"**Diagnóstico:** {analisis.get('diagnostico','')}")
                st.markdown(f"**Acción para hoy:** {analisis.get('accion_hoy','')}")
                st.markdown(f"**Proyección 3 meses:** {analisis.get('proyeccion_3_meses','')}")
                if analisis.get("estrategias"):
                    st.markdown("**Estrategias:**")
                    for e in analisis["estrategias"]:
                        st.markdown(f"- {e}")
            except Exception as ex:
                st.error(f"Error: {ex}")
    st.markdown("---")
    pagos = db.obtener_pagos()
    if pagos:
        df = pd.DataFrame(pagos)[["cliente_nombre","monto","fecha","metodo","notas"]]
        df.columns = ["Cliente","Monto","Fecha","Método","Notas"]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay pagos registrados.")

elif pagina == "📅 Planificación":
    st.title("📅 Planificación de Contenido")
    st.markdown("Organiza el contenido mensual de cada cliente")
    st.markdown("---")
    clientes = db.obtener_clientes()
    if not clientes:
        st.info("Primero agrega clientes.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            opciones = {c["nombre"]: c for c in clientes}
            cliente_sel = st.selectbox("Selecciona cliente", list(opciones.keys()))
            cliente_data = opciones[cliente_sel]
        with col2:
            mes = st.selectbox("Mes", ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"])
        if st.button("🤖 Generar plan de contenido con IA", type="primary"):
            with st.spinner("Generando plan mensual..."):
                try:
                    plan = ai.generar_plan_contenido(cliente_sel, cliente_data["servicio"], mes)
                    st.success("✅ Plan generado")
                    for semana, posts in plan.items():
                        if semana.startswith("semana") and isinstance(posts, list):
                            num = semana.split("_")[1]
                            st.subheader(f"Semana {num}")
                            st.dataframe(pd.DataFrame(posts), use_container_width=True)
                    if plan.get("estrategia_general"):
                        st.info(f"**Estrategia general:** {plan['estrategia_general']}")
                    db.guardar_contenido(cliente_data["id"], "plan_mensual", cliente_data["servicio"], json.dumps(plan, ensure_ascii=False))
                except Exception as ex:
                    st.error(f"Error: {ex}")

elif pagina == "🔍 Tendencias":
    st.title("🔍 Agente de Tendencias")
    st.markdown("---")
    if st.button("🔄 Investigar tendencias con IA", type="primary"):
        with st.spinner("Investigando..."):
            try:
                resultado = ai.investigar_tendencias()
                for t in resultado.get("tendencias",[]):
                    db.guardar_tendencia(t["titulo"], t["descripcion"], t["oportunidad"])
                st.success("✅ Tendencias actualizadas")
                st.info(f"**Resumen:** {resultado.get('resumen','')}")
                st.warning(f"**Acción inmediata:** {resultado.get('accion_inmediata','')}")
            except Exception as ex:
                st.error(f"Error: {ex}")
    st.markdown("---")
    tendencias = db.obtener_tendencias()
    if tendencias:
        for t in tendencias:
            with st.container(border=True):
                st.markdown(f"#### {t['titulo']}")
                st.write(t["descripcion"])
                st.success(f"💡 {t['oportunidad']}")
                st.caption(f"📅 {t['fecha'][:10]}")
    else:
        st.info("Haz click en el botón para investigar tendencias.")

elif pagina == "📧 Notificaciones":
    st.title("📧 Centro de Notificaciones")
    st.markdown("---")
    clientes = db.obtener_clientes()
    pendientes = [c for c in clientes if c["estado"] == "pendiente"]
    st.subheader(f"⚠️ Clientes pendientes ({len(pendientes)})")
    if not pendientes:
        st.success("✅ No hay cobros pendientes.")
    else:
        for c in pendientes:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.markdown(f"**{c['nombre']}** — {c['servicio']}")
                    st.caption(f"${c['mensualidad']}/mes · {c['email'] or 'Sin email'}")
                with col2:
                    if c["email"] and st.button("📧 Recordatorio", key=f"rec_{c['id']}"):
                        ok, msg = notifications.email_recordatorio_pago(c["nombre"], c["email"], c["mensualidad"], c["servicio"], c["fecha_pago"] or "fecha acordada")
                        st.success("Enviado") if ok else st.error(msg)
                with col3:
                    if st.button("🤖 Mensaje IA", key=f"ia_{c['id']}"):
                        with st.spinner("Generando..."):
                            try:
                                msg = ai.generar_mensaje_cobro(c["nombre"], c["mensualidad"], c["servicio"])
                                st.text_area("Copia:", msg, key=f"msg_{c['id']}")
                            except Exception as ex:
                                st.error(f"Error: {ex}")

elif pagina == "⚙️ Configuración":
    st.title("⚙️ Configuración")
    st.markdown("---")
    st.subheader("🔑 Secrets de Streamlit Cloud")
    st.info("Ve a tu app en Streamlit Cloud → Settings → Secrets y agrega:")
    st.code("""
ANTHROPIC_API_KEY = "sk-ant-..."
SMTP_EMAIL = "tucorreo@gmail.com"
SMTP_PASSWORD = "tu-app-password-gmail"
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "tu-service-role-key"
    """, language="toml")
    clientes = db.obtener_clientes()
    pagos = db.obtener_pagos()
    col1, col2 = st.columns(2)
    col1.metric("Clientes", len(clientes))
    col2.metric("Pagos", len(pagos))
SMTP_EMAIL = "tucorreo@gmail.com"
SMTP_PASSWORD = "tu-app-password-gmail"
    """, language="toml")
    clientes = db.obtener_clientes()
    pagos = db.obtener_pagos()
    col1, col2 = st.columns(2)
    col1.metric("Clientes", len(clientes))
    col2.metric("Pagos", len(pagos))

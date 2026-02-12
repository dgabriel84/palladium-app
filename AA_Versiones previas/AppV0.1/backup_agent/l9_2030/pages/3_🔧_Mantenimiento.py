"""
Página de Mantenimiento de Reservas - Empleados
Panel para consultar reservas, ver riesgo de cancelación y gestionar retención.

Autor: Grupo 4 - TFM Palladium
Fecha: Febrero 2026
"""

import streamlit as st
import pandas as pd
import datetime
import sys
import os

# Configuración de rutas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones del módulo principal
try:
    from app import cargar_reservas_csv, buscar_reserva_por_id, actualizar_reserva_csv, HISTORIAL_RESERVAS_PATH
    from app import COLOR_VERDE_OSCURO, COLOR_DORADO, COLOR_GRIS, COLOR_CREMA, COLOR_BEIGE, COLOR_BLANCO
except ImportError:
    st.error("Error importando módulos. Ejecuta desde el directorio principal.")
    st.stop()

# Configuración de página
st.set_page_config(
    page_title="Mantenimiento Reservas - Palladium",
    page_icon="🔧",
    layout="wide"
)

# Colores para riesgo
def color_riesgo(prob):
    """Devuelve color según nivel de riesgo"""
    if prob >= 0.7:
        return "#dc3545"  # Rojo - Alto riesgo
    elif prob >= 0.4:
        return "#ffc107"  # Amarillo - Riesgo medio
    else:
        return "#28a745"  # Verde - Bajo riesgo

def etiqueta_riesgo(prob):
    """Devuelve etiqueta de riesgo"""
    if prob >= 0.7:
        return "🔴 ALTO"
    elif prob >= 0.4:
        return "🟡 MEDIO"
    else:
        return "🟢 BAJO"

# Título
st.markdown(f"""
<h1 style="color: {COLOR_VERDE_OSCURO}; font-weight: 300;">🔧 Mantenimiento de Reservas</h1>
<p style="color: {COLOR_GRIS};">Panel de gestión para empleados - Consulta y retención de clientes</p>
""", unsafe_allow_html=True)

st.markdown("---")

# Tabs principales
tab_listado, tab_buscar, tab_estadisticas = st.tabs(["📋 Listado de Reservas", "🔍 Buscar Reserva", "📊 Estadísticas"])

# -------------------------------------------------------------------------------
# TAB 1: LISTADO DE RESERVAS
# -------------------------------------------------------------------------------
with tab_listado:
    # Cargar reservas
    df_reservas = cargar_reservas_csv()
    
    if df_reservas.empty:
        st.info("No hay reservas registradas todavía. Las reservas se guardarán automáticamente al confirmarlas.")
    else:
        # Filtros
        st.subheader("Filtros")
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            filtro_riesgo = st.selectbox(
                "Nivel de Riesgo",
                ["Todos", "🔴 Alto (≥70%)", "🟡 Medio (40-70%)", "🟢 Bajo (<40%)"]
            )
        
        with col_f2:
            estados_unicos = ["Todos"] + list(df_reservas['estado'].unique())
            filtro_estado = st.selectbox("Estado", estados_unicos)
        
        with col_f3:
            hoteles_unicos = ["Todos"] + list(df_reservas['hotel'].unique())
            filtro_hotel = st.selectbox("Hotel", hoteles_unicos)
        
        with col_f4:
            ordenar_por = st.selectbox(
                "Ordenar por",
                ["Riesgo (mayor primero)", "Fecha creación (reciente)", "Llegada (próxima)", "Valor (mayor)"]
            )
        
        # Aplicar filtros
        df_filtrado = df_reservas.copy()
        
        if filtro_riesgo == "🔴 Alto (≥70%)":
            df_filtrado = df_filtrado[df_filtrado['prob_cancelacion'] >= 0.7]
        elif filtro_riesgo == "🟡 Medio (40-70%)":
            df_filtrado = df_filtrado[(df_filtrado['prob_cancelacion'] >= 0.4) & (df_filtrado['prob_cancelacion'] < 0.7)]
        elif filtro_riesgo == "🟢 Bajo (<40%)":
            df_filtrado = df_filtrado[df_filtrado['prob_cancelacion'] < 0.4]
        
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado]
        
        if filtro_hotel != "Todos":
            df_filtrado = df_filtrado[df_filtrado['hotel'] == filtro_hotel]
        
        # Ordenar
        if ordenar_por == "Riesgo (mayor primero)":
            df_filtrado = df_filtrado.sort_values('prob_cancelacion', ascending=False)
        elif ordenar_por == "Fecha creación (reciente)":
            df_filtrado = df_filtrado.sort_values('fecha_creacion', ascending=False)
        elif ordenar_por == "Llegada (próxima)":
            df_filtrado = df_filtrado.sort_values('llegada', ascending=True)
        elif ordenar_por == "Valor (mayor)":
            df_filtrado = df_filtrado.sort_values('valor_total', ascending=False)
        
        st.markdown("---")
        
        # Estadísticas rápidas
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Reservas", len(df_filtrado))
        with col_s2:
            alto_riesgo = len(df_filtrado[df_filtrado['prob_cancelacion'] >= 0.7])
            st.metric("🔴 Alto Riesgo", alto_riesgo)
        with col_s3:
            valor_total = df_filtrado['valor_total'].sum()
            st.metric("Valor en Riesgo", f"{valor_total:,.0f}€")
        with col_s4:
            prob_media = df_filtrado['prob_cancelacion'].mean() * 100 if not df_filtrado.empty else 0
            st.metric("Prob. Media", f"{prob_media:.1f}%")
        
        st.markdown("---")
        
        # Listado de reservas
        st.subheader(f"Reservas ({len(df_filtrado)})")
        
        for idx, row in df_filtrado.iterrows():
            prob = row['prob_cancelacion']
            color = color_riesgo(prob)
            etiqueta = etiqueta_riesgo(prob)
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: {COLOR_BEIGE}; padding: 0.5rem; border-radius: 4px; text-align: center;">
                        <p style="margin: 0; font-size: 0.7rem; color: {COLOR_GRIS};">Código</p>
                        <p style="margin: 0; font-weight: 600; font-size: 0.9rem;">{row['id_reserva']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    llegada_str = row['llegada'].strftime('%d/%m/%Y') if pd.notna(row['llegada']) else 'N/A'
                    st.markdown(f"""
                    <p style="margin: 0; font-size: 0.85rem;"><strong>{row['hotel']}</strong></p>
                    <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">{row['habitacion']}</p>
                    <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">📅 {llegada_str} · {row['noches']} noches</p>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <p style="margin: 0; font-size: 0.85rem;">{row['cliente_nombre']}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: {COLOR_GRIS};">{row['cliente_email']}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: {COLOR_GRIS};">🌍 {row['cliente_pais']}</p>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 0.5rem; border-radius: 8px; text-align: center;">
                        <p style="margin: 0; font-size: 1.2rem; font-weight: 600;">{prob*100:.0f}%</p>
                        <p style="margin: 0; font-size: 0.7rem;">{etiqueta.split()[0]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col5:
                    st.markdown(f"""
                    <p style="margin: 0; font-size: 1.1rem; font-weight: 600; color: {COLOR_VERDE_OSCURO};">{row['valor_total']:,.0f}€</p>
                    <p style="margin: 0; font-size: 0.75rem; color: {COLOR_GRIS};">Estado: {row['estado']}</p>
                    """, unsafe_allow_html=True)
                    
                    # Botón de acción solo si alto riesgo
                    if prob >= 0.4:
                        if st.button("📧 Ofrecer Retención", key=f"ret_{row['id_reserva']}"):
                            st.session_state[f"mostrar_retencion_{row['id_reserva']}"] = True
                
                # Panel de retención expandible
                if st.session_state.get(f"mostrar_retencion_{row['id_reserva']}", False):
                    with st.expander("🎁 Configurar Oferta de Retención", expanded=True):
                        col_of1, col_of2 = st.columns(2)
                        with col_of1:
                            tipo_oferta = st.selectbox(
                                "Tipo de oferta",
                                ["Descuento 10%", "Descuento 15%", "Descuento 20%", 
                                 "Upgrade habitación", "Late checkout", "Cena gratis",
                                 "Spa gratis", "Traslado gratis"],
                                key=f"oferta_{row['id_reserva']}"
                            )
                        with col_of2:
                            nota = st.text_input("Nota adicional", key=f"nota_{row['id_reserva']}")
                        
                        if st.button("✅ Registrar y Enviar Oferta", key=f"enviar_{row['id_reserva']}"):
                            # Actualizar en CSV
                            oferta_completa = f"{tipo_oferta}" + (f" - {nota}" if nota else "")
                            actualizar_reserva_csv(str(row['id_reserva']), 'oferta_retencion', oferta_completa)
                            st.success(f"✅ Oferta registrada: {oferta_completa}")
                            st.session_state[f"mostrar_retencion_{row['id_reserva']}"] = False
                            st.rerun()
                
                st.markdown("---")

# -------------------------------------------------------------------------------
# TAB 2: BUSCAR RESERVA
# -------------------------------------------------------------------------------
with tab_buscar:
    st.subheader("🔍 Buscar por Código de Reserva")
    
    codigo_buscar = st.text_input("Introduce el código de reserva", placeholder="Ej: 704970109601")
    
    if st.button("Buscar", type="primary"):
        if codigo_buscar:
            reserva = buscar_reserva_por_id(codigo_buscar)
            if reserva:
                prob = reserva.get('prob_cancelacion', 0)
                color = color_riesgo(prob)
                etiqueta = etiqueta_riesgo(prob)
                
                st.success("✅ Reserva encontrada")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: {COLOR_CREMA}; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                        <h3 style="margin: 0 0 1rem 0; color: {COLOR_VERDE_OSCURO};">Código: {reserva.get('id_reserva', '')}</h3>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div>
                                <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">Cliente</p>
                                <p style="margin: 0; font-weight: 600;">{reserva.get('cliente_nombre', '')}</p>
                                <p style="margin: 0; font-size: 0.85rem;">{reserva.get('cliente_email', '')}</p>
                                <p style="margin: 0; font-size: 0.85rem;">{reserva.get('cliente_pais', '')}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">Hotel</p>
                                <p style="margin: 0; font-weight: 600;">{reserva.get('hotel', '')}</p>
                                <p style="margin: 0; font-size: 0.85rem;">{reserva.get('habitacion', '')}</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">Fechas</p>
                                <p style="margin: 0;">Llegada: {reserva.get('llegada', '')}</p>
                                <p style="margin: 0;">{reserva.get('noches', 0)} noches</p>
                            </div>
                            <div>
                                <p style="margin: 0; font-size: 0.8rem; color: {COLOR_GRIS};">Huéspedes</p>
                                <p style="margin: 0;">{reserva.get('adultos', 0)} adultos, {reserva.get('ninos', 0)} niños</p>
                                <p style="margin: 0; font-size: 0.85rem;">Fidelidad: {reserva.get('fidelidad', 'N/A')}</p>
                            </div>
                        </div>
                        
                        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {COLOR_BEIGE};">
                            <p style="margin: 0; font-size: 1.3rem; font-weight: 600; color: {COLOR_VERDE_OSCURO};">
                                Valor: {reserva.get('valor_total', 0):,.0f}€
                            </p>
                            <p style="margin: 0; font-size: 0.85rem; color: {COLOR_GRIS};">
                                Estado: {reserva.get('estado', '')} | Creada: {reserva.get('fecha_creacion', '')}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
                        <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Probabilidad de Cancelación</p>
                        <p style="margin: 0.5rem 0; font-size: 3rem; font-weight: 600;">{prob*100:.0f}%</p>
                        <p style="margin: 0; font-size: 1.2rem;">{etiqueta}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if reserva.get('oferta_retencion'):
                        st.markdown(f"""
                        <div style="background: {COLOR_DORADO}; color: white; padding: 1rem; border-radius: 8px; margin-top: 1rem; text-align: center;">
                            <p style="margin: 0; font-size: 0.8rem;">Oferta enviada</p>
                            <p style="margin: 0; font-weight: 600;">{reserva.get('oferta_retencion')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("❌ No se encontró ninguna reserva con ese código")
        else:
            st.warning("Introduce un código de reserva")

# -------------------------------------------------------------------------------
# TAB 3: ESTADÍSTICAS
# -------------------------------------------------------------------------------
with tab_estadisticas:
    df_reservas = cargar_reservas_csv()
    
    if df_reservas.empty:
        st.info("No hay datos suficientes para mostrar estadísticas.")
    else:
        st.subheader("📊 Resumen de Reservas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reservas", len(df_reservas))
        with col2:
            valor_total = df_reservas['valor_total'].sum()
            st.metric("Valor Total", f"{valor_total:,.0f}€")
        with col3:
            alto_riesgo = len(df_reservas[df_reservas['prob_cancelacion'] >= 0.7])
            st.metric("Alto Riesgo", f"{alto_riesgo} ({alto_riesgo/len(df_reservas)*100:.1f}%)")
        with col4:
            ofertas = len(df_reservas[df_reservas['oferta_retencion'].notna() & (df_reservas['oferta_retencion'] != '')])
            st.metric("Ofertas Enviadas", ofertas)
        
        st.markdown("---")
        
        # Distribución por riesgo
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("Distribución por Nivel de Riesgo")
            alto = len(df_reservas[df_reservas['prob_cancelacion'] >= 0.7])
            medio = len(df_reservas[(df_reservas['prob_cancelacion'] >= 0.4) & (df_reservas['prob_cancelacion'] < 0.7)])
            bajo = len(df_reservas[df_reservas['prob_cancelacion'] < 0.4])
            
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                    <div style="width: 20px; height: 20px; background: #dc3545; border-radius: 4px; margin-right: 10px;"></div>
                    <span>Alto (≥70%): <strong>{alto}</strong> reservas ({alto/len(df_reservas)*100:.1f}%)</span>
                </div>
                <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                    <div style="width: 20px; height: 20px; background: #ffc107; border-radius: 4px; margin-right: 10px;"></div>
                    <span>Medio (40-70%): <strong>{medio}</strong> reservas ({medio/len(df_reservas)*100:.1f}%)</span>
                </div>
                <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                    <div style="width: 20px; height: 20px; background: #28a745; border-radius: 4px; margin-right: 10px;"></div>
                    <span>Bajo (<40%): <strong>{bajo}</strong> reservas ({bajo/len(df_reservas)*100:.1f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g2:
            st.subheader("Valor en Riesgo")
            valor_alto = df_reservas[df_reservas['prob_cancelacion'] >= 0.7]['valor_total'].sum()
            valor_medio = df_reservas[(df_reservas['prob_cancelacion'] >= 0.4) & (df_reservas['prob_cancelacion'] < 0.7)]['valor_total'].sum()
            valor_bajo = df_reservas[df_reservas['prob_cancelacion'] < 0.4]['valor_total'].sum()
            
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="background: #dc3545; color: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span>Alto Riesgo: <strong>{valor_alto:,.0f}€</strong></span>
                </div>
                <div style="background: #ffc107; color: black; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span>Riesgo Medio: <strong>{valor_medio:,.0f}€</strong></span>
                </div>
                <div style="background: #28a745; color: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span>Bajo Riesgo: <strong>{valor_bajo:,.0f}€</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabla resumen por hotel
        st.subheader("Resumen por Hotel")
        resumen_hotel = df_reservas.groupby('hotel').agg({
            'id_reserva': 'count',
            'valor_total': 'sum',
            'prob_cancelacion': 'mean'
        }).rename(columns={
            'id_reserva': 'Reservas',
            'valor_total': 'Valor Total',
            'prob_cancelacion': 'Prob. Media'
        })
        resumen_hotel['Prob. Media'] = (resumen_hotel['Prob. Media'] * 100).round(1).astype(str) + '%'
        resumen_hotel['Valor Total'] = resumen_hotel['Valor Total'].apply(lambda x: f"{x:,.0f}€")
        st.dataframe(resumen_hotel, use_container_width=True)

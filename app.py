"""
Interfaz web sencilla para buscar clientes potenciales (pymes) en Google Maps.
Para correrla:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import os

# 1. La configuración de la página SIEMPRE debe ir primero
st.set_page_config(page_title="Buscador de Clientes Potenciales", page_icon="🔎", layout="wide")

# 2. Luego sí definimos y ejecutamos la instalación
@st.cache_resource
def install_playwright():
    os.system("python -m playwright install chromium")

install_playwright()

from scraper import scrape_places

st.title("🔎 Buscador de Clientes Potenciales")
st.caption(
    "Busca pymes en Google Maps y filtra los mejores prospectos para ofrecerles "
    "tus servicios de análisis de datos."
)

with st.form("busqueda_form"):
    col1, col2 = st.columns(2)
    with col1:
        rubro = st.text_input("Tipo de negocio", placeholder="Ej: panaderías, restaurantes, ferreterías")
    with col2:
        ciudad = st.text_input("Ciudad", placeholder="Ej: Cali, Colombia")
    total = st.slider("Cantidad de negocios a buscar", min_value=5, max_value=100, value=20, step=5)
    submitted = st.form_submit_button("Buscar", use_container_width=True)

if submitted:
    if not rubro or not ciudad:
        st.warning("Completa el tipo de negocio y la ciudad antes de buscar.")
    else:
        query = f"{rubro} en {ciudad}"
        status_box = st.empty()
        log_lines = []

        def progress(msg: str):
            log_lines.append(msg)
            status_box.info("\n".join(log_lines[-6:]))

        with st.spinner(f"Buscando '{query}'... esto puede tardar varios minutos, no cierres la ventana."):
            places = scrape_places(query, total, progress_callback=progress)

        status_box.empty()

        if not places:
            st.error("No se encontraron resultados. Intenta con otro término de búsqueda.")
        else:
            df = pd.DataFrame([p.__dict__ for p in places])
            df["tiene_sitio_web"] = df["website"].apply(lambda x: "No" if not x else "Sí")
            st.session_state["df"] = df
            st.session_state["query"] = query

if "df" in st.session_state:
    df = st.session_state["df"]
    st.success(f"Se encontraron {len(df)} negocios para '{st.session_state.get('query', '')}'.")

    st.subheader("Filtrar prospectos")
    colf1, colf2 = st.columns(2)
    with colf1:
        solo_sin_web = st.checkbox(
            "Mostrar solo negocios SIN sitio web",
            help="Suelen ser mejores prospectos: es probable que tampoco tengan dashboards ni análisis de datos.",
        )
    with colf2:
        min_resenas = st.number_input("Mínimo de reseñas en Google", min_value=0, value=0)

    df_filtrado = df.copy()
    if solo_sin_web:
        df_filtrado = df_filtrado[df_filtrado["tiene_sitio_web"] == "No"]
    if "reviews_count" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["reviews_count"].fillna(0) >= min_resenas]

    st.write(f"**{len(df_filtrado)} negocios** cumplen los filtros seleccionados.")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Descargar lista en CSV",
        data=csv,
        file_name="clientes_potenciales.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.caption(
        "Consejo: usa esta lista para contactar por WhatsApp o llamada, mencionando algo "
        "puntual del negocio (ej. sus reseñas o su falta de sitio web) para personalizar tu oferta."
    )

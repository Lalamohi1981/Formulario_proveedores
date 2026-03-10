import streamlit as st
import psycopg2
import os
import pandas as pd
import re
from datetime import datetime

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================

st.set_page_config(
    page_title="Portal Proveedores - GreenMovil",
    page_icon="🟢",
    layout="wide"
)

# =========================
# ESTILOS
# =========================

st.markdown("""
<style>

.block-container {
    padding-top: 2rem !important;
}

h2 {
    font-size: 34px !important;
    font-weight: 700 !important;
}

label {
    font-size: 18px !important;
}

input {
    font-size: 17px !important;
}

.stButton>button {
    background-color: #A1C42A;
    color: white;
    border-radius: 8px;
    padding: 0.7em 1.6em;
}

.stButton>button:hover {
    background-color: #00594E;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown(
"<div style='background-color:#A1C42A; height:4px; margin-bottom:20px;'></div>",
unsafe_allow_html=True
)

col_title, col_logo = st.columns([4,1])

with col_title:

    st.markdown("## Portal Oficial de Registro de Proveedores")

    st.markdown("""
    Este portal ha sido dispuesto para el registro formal de proveedores de **GreenMóvil S.A.S.**
    """)

    st.markdown(
        f"<small>Fecha del sistema: {datetime.now().strftime('%d/%m/%Y')}</small>",
        unsafe_allow_html=True
    )

with col_logo:
    st.image("logo.png", use_container_width=True)

st.divider()

# =========================
# CONEXIÓN BD
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

# =========================
# PASSWORD COMPRAS
# =========================

PASSWORD_COMPRAS = os.getenv("PASSWORD_COMPRAS","compras123")

# =========================
# VALIDACIÓN EMAIL
# =========================

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email)

# =========================
# TABS
# =========================

tab1, tab2 = st.tabs(["📝 Registro Proveedor", "🔐 Zona Compras"])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    if "accionistas" not in st.session_state:
        st.session_state.accionistas = []

    if "junta" not in st.session_state:
        st.session_state.junta = []

    if "mensaje_ok" in st.session_state and st.session_state.mensaje_ok:
        st.success("La información fue registrada correctamente.")
        st.session_state.mensaje_ok = False

    st.subheader("🏢 Información de la empresa")

    col1,col2,col3 = st.columns([3,2,1])

    with col1:
        nombre_empresa = st.text_input("Nombre empresa", key="nombre_empresa")

    with col2:
        nit = st.text_input("NIT", key="nit")

    with col3:
        dv = st.text_input("DV", max_chars=1, key="dv")

    correo = st.text_input("Correo electrónico", key="correo")

    st.divider()

    st.subheader("👤 Representante legal")

    col1,col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre representante", key="nombre_rep")
        tipo_documento = st.selectbox("Tipo documento", ["CC","CE","NIT","Pasaporte"])

    with col2:
        cargo = st.selectbox("Cargo", ["Representante Legal"])
        numero_documento = st.text_input("Número documento", key="numero_documento")

    # =========================
    # ACCIONISTAS
    # =========================

    st.divider()
    st.subheader("📊 Accionistas")

    for i in range(len(st.session_state.accionistas)):

        col1,col2,col3,col4 = st.columns([3,2,2,1])

        with col1:
            st.text_input("Nombre",key=f"acc_nombre_{i}")

        with col2:
            st.selectbox("Tipo",["CC","CE","Pasaporte"],key=f"acc_tipo_{i}")

        with col3:
            st.text_input("Documento",key=f"acc_doc_{i}")

        with col4:
            if st.button("❌",key=f"del_acc_{i}"):
                st.session_state.accionistas.pop(i)
                st.rerun()

    if st.button("➕ Agregar accionista"):
        st.session_state.accionistas.append({})

    # =========================
    # JUNTA
    # =========================

    st.divider()
    st.subheader("🏛 Junta directiva")

    for i in range(len(st.session_state.junta)):

        col1,col2,col3,col4 = st.columns([3,2,2,1])

        with col1:
            st.text_input("Nombre",key=f"jd_nombre_{i}")

        with col2:
            st.selectbox("Tipo",["CC","CE","Pasaporte"],key=f"jd_tipo_{i}")

        with col3:
            st.text_input("Documento",key=f"jd_doc_{i}")

        with col4:
            if st.button("❌",key=f"del_jd_{i}"):
                st.session_state.junta.pop(i)
                st.rerun()

    if st.button("➕ Agregar miembro junta"):
        st.session_state.junta.append({})

    # =========================
    # BOTÓN REGISTRO
    # =========================

    if st.button("Registrar información"):

        if not nombre_empresa.strip():
            st.error("Debe ingresar empresa")

        elif not nit.strip():
            st.error("Debe ingresar NIT")

        elif not nombre.strip():
            st.error("Debe ingresar representante")

        elif not validar_email(correo):
            st.error("Correo inválido")

        else:

           
            try:

                conn = conectar()   
                cursor = conn.cursor()

                cursor.execute("""
                INSERT INTO proveedores
                (nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,(nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo))

                for i in range(len(st.session_state.accionistas)):

                    acc_nombre = st.session_state.get(f"acc_nombre_{i}")
                    acc_tipo = st.session_state.get(f"acc_tipo_{i}")
                    acc_doc = st.session_state.get(f"acc_doc_{i}")

                    if acc_nombre and acc_doc:

                        cursor.execute("""
                        INSERT INTO proveedores
                        (nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,(nombre_empresa,nit,dv,acc_tipo,acc_doc,acc_nombre.upper(),"ACCIONISTA",correo))

                for i in range(len(st.session_state.junta)):

                    jd_nombre = st.session_state.get(f"jd_nombre_{i}")
                    jd_tipo = st.session_state.get(f"jd_tipo_{i}")
                    jd_doc = st.session_state.get(f"jd_doc_{i}")

                    if jd_nombre and jd_doc:

                        cursor.execute("""
                        INSERT INTO proveedores
                        (nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """,(nombre_empresa,nit,dv,jd_tipo,jd_doc,jd_nombre.upper(),"MIEMBRO JUNTA",correo))

                conn.commit()
                conn.close()

                # limpiar listas
                st.session_state.accionistas = []
                st.session_state.junta = []

                # limpiar campos formulario
                for campo in [
                    "nombre_empresa",
                    "nit",
                    "dv",
                    "correo",
                    "nombre_rep",
                    "numero_documento"
                ]:
                    if campo in st.session_state:
                        del st.session_state[campo]

                st.session_state.mensaje_ok = True
                st.rerun()

            except Exception as e:

                if "unique_persona_empresa" in str(e):
                    st.warning("⚠️ Esta persona ya está registrada para esta empresa.")
                else:
                    st.error(f"Error al guardar: {e}")

     

# =====================================================
# TAB 2 - ZONA COMPRAS
# =====================================================

with tab2:

    st.subheader("Base de proveedores registrados")

    # 🔐 contraseña desde Secrets o fallback local
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Compras2026")

    password = st.text_input("Ingrese contraseña", type="password")

    if password == ADMIN_PASSWORD:

        try:

            conn = conectar()

            df = pd.read_sql("""
                SELECT
                    id,
                    nombre_empresa,
                    nit,
                    nombre,
                    cargo,
                    correo,
                    fecha_registro AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota' AS fecha_registro
                FROM proveedores
                ORDER BY fecha_registro DESC
                """, conn)

            conn.close()

            st.dataframe(df, use_container_width=True)

            st.caption(f"Total registros: {len(df)}")

            # -------------------------------------------------
            # DESCARGA CSV
            # -------------------------------------------------

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Descargar base de proveedores",
                data=csv,
                file_name="base_proveedores.csv",
                mime="text/csv"
            )

        except Exception as e:

            st.error(f"Error cargando base: {e}")

    elif password != "":
        st.error("Contraseña incorrecta")
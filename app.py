import streamlit as st
import psycopg2
import os
import pandas as pd
import re
from io import BytesIO

# =========================
# CONFIGURACIÓN DE PÁGINA
# =========================

st.set_page_config(
    page_title="Formulario Proveedores - GreenMovil",
    page_icon="🟢",
    layout="wide"
)

# =========================
# ESTILOS PERSONALIZADOS
# =========================

st.markdown("""
<style>
body {
    background-color: #F6F8FC;
}

h1, h2, h3 {
    color: #252423;
}

.stTabs [role="tab"] {
    font-size: 16px;
    font-weight: 600;
}

.stButton>button {
    background-color: #A1C42A;
    color: white;
    border-radius: 8px;
    padding: 0.5em 1em;
    border: none;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #00594E;
    color: white;
}

[data-testid="stDataFrame"] {
    border-radius: 10px;
    background-color: white;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGO CENTRADO
# =========================

col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])

with col_logo2:
    st.image("logo.png", width=250)

# =========================
# CONEXIÓN BD
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

# =========================
# VALIDACIÓN EMAIL
# =========================

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email)

# =========================
# TABS PRINCIPALES
# =========================

tab1, tab2 = st.tabs(["📝 Registro Proveedor", "🔐 Zona Compras"])

# =====================================================
# TAB 1 - FORMULARIO
# =====================================================

with tab1:
    with st.container(border=True):

        st.header("Formulario de Registro")

        if "reset" not in st.session_state:
            st.session_state.reset = False

        if st.session_state.reset:
            st.session_state.nombre_empresa = ""
            st.session_state.nit = ""
            st.session_state.representante = ""
            st.session_state.numero_documento = ""
            st.session_state.correo = ""
            st.session_state.reset = False

        col1, col2 = st.columns(2)

        with col1:
            nombre_empresa = st.text_input("Nombre de la empresa", key="nombre_empresa")
            nit = st.text_input("NIT", key="nit")
            representante = st.text_input("Representante legal", key="representante")

        with col2:
            tipo_documento = st.selectbox("Tipo documento", ["Cédula", "NIT", "Pasaporte"])
            numero_documento = st.text_input("Número documento", key="numero_documento")
            correo = st.text_input("Correo electrónico", key="correo")

        colb1, colb2 = st.columns(2)

        with colb1:
            enviar = st.button("Enviar")

        with colb2:
            limpiar = st.button("Limpiar")

        # BOTÓN LIMPIAR
        if limpiar:
            st.session_state.reset = True
            st.rerun()

        # BOTÓN ENVIAR
        if enviar:

            if (
                not nombre_empresa.strip()
                or not nit.strip()
                or not representante.strip()
                or not tipo_documento.strip()
                or not numero_documento.strip()
                or not correo.strip()
            ):
                st.error("Todos los campos son obligatorios")

            elif not nit.isdigit():
                st.error("El NIT debe contener solo números")

            elif not numero_documento.isdigit():
                st.error("El número de documento debe contener solo números")

            elif not validar_email(correo):
                st.error("El correo electrónico no es válido")

            else:
                nombre_empresa = nombre_empresa.strip().upper()
                representante = representante.strip().upper()

                try:
                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT COUNT(*) FROM proveedores WHERE nit = %s",
                        (nit,)
                    )
                    cantidad = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        INSERT INTO proveedores 
                        (nombre_empresa, nit, representante_legal, tipo_documento, numero_documento, correo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (nombre_empresa, nit, representante, tipo_documento, numero_documento, correo)
                    )

                    conn.commit()
                    cursor.close()
                    conn.close()

                    if cantidad > 0:
                        st.success("Información actualizada correctamente. Se creó nueva versión.")
                    else:
                        st.success("Proveedor registrado correctamente.")

                    st.session_state.reset = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# =====================================================
# TAB 2 - ZONA COMPRAS
# =====================================================

with tab2:
    with st.container(border=True):

        st.header("Zona Interna - Compras")

        if "auth" not in st.session_state:
            st.session_state.auth = False

        password = st.text_input("Ingrese contraseña", type="password")

        if password == os.getenv("ADMIN_PASSWORD"):
            st.session_state.auth = True

        if st.session_state.auth:
            try:
                conn = conectar()

                df = pd.read_sql(
                    """
                    SELECT DISTINCT ON (nit) *
                    FROM proveedores
                    ORDER BY nit, fecha_registro DESC
                    """,
                    conn
                )

                conn.close()

                st.success("Acceso concedido")
                st.dataframe(df, use_container_width=True)

                buffer = BytesIO()
                df.to_excel(buffer, index=False)
                buffer.seek(0)

                st.download_button(
                    label="📥 Descargar Excel",
                    data=buffer,
                    file_name="proveedores.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error al consultar datos: {e}")

        elif password != "":
            st.error("Contraseña incorrecta")

import streamlit as st
import psycopg2
import os
import pandas as pd
import re
from io import BytesIO
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
# FRANJA VERDE SUPERIOR
# =========================

st.markdown("""
<div style='background-color:#A1C42A; height:6px; margin-bottom:20px;'></div>
""", unsafe_allow_html=True)

# =========================
# LOGO
# =========================

col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])

with col_logo2:
    st.image("logo.png", width=250)

# =========================
# ENCABEZADO INSTITUCIONAL
# =========================

st.markdown(f"""
<div style='text-align: center; margin-top: 10px; margin-bottom: 10px;'>

    <h1 style='color:#252423; font-weight:700; margin-bottom: 8px;'>
        Portal Oficial de Registro de Proveedores
    </h1>

    <p style='color:#605E5C; font-size:15px; max-width:850px; margin:auto; line-height:1.6;'>
        Este portal ha sido dispuesto para la actualización y registro formal de proveedores 
        de GreenMóvil S.A.S. La información suministrada será utilizada exclusivamente para 
        fines administrativos, contractuales y de validación interna.
        <br><br>
        En caso de haber realizado un registro previo, podrá actualizar sus datos mediante 
        un nuevo envío del formulario.
    </p>

    <p style='color:#605E5C; font-size:13px; margin-top:10px;'>
        Fecha del sistema: {datetime.now().strftime("%d/%m/%Y")}
        &nbsp;&nbsp;|&nbsp;&nbsp;
        Versión del sistema: 1.0
    </p>

</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #C8C6C4;'>", unsafe_allow_html=True)

# =========================
# CONEXIÓN BASE DE DATOS
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
# TABS
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

        if limpiar:
            st.session_state.reset = True
            st.rerun()

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

                    st.success("Registro realizado correctamente.")
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

                st.success("Acceso autorizado")
                st.dataframe(df, use_container_width=True)

                buffer = BytesIO()
                df.to_excel(buffer, index=False)
                buffer.seek(0)

                st.download_button(
                    label="Descargar base en Excel",
                    data=buffer,
                    file_name="proveedores.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error al consultar datos: {e}")

        elif password != "":
            st.error("Contraseña incorrecta")

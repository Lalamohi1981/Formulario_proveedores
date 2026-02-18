import streamlit as st
import psycopg2
import os
import pandas as pd
import re
from io import BytesIO

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
# FORMULARIO PROVEEDORES
# =========================

st.title("Formulario Proveedores")
st.write("Registro de proveedores")

nombre_empresa = st.text_input("Nombre de la empresa")
nit = st.text_input("NIT")
representante = st.text_input("Nombre representante legal")
tipo_documento = st.selectbox("Tipo documento", ["Cédula", "NIT", "Pasaporte"])
numero_documento = st.text_input("Número documento")
correo = st.text_input("Correo electrónico")

if st.button("Enviar"):

    # 🔐 VALIDACIONES
    if (
        not nombre_empresa.strip()
        or not nit.strip()
        or not representante.strip()
        or not tipo_documento.strip()
        or not numero_documento.strip()
        or not correo.strip()
    ):
        st.error("Todos los campos son obligatorios")

    elif not validar_email(correo):
        st.error("El correo electrónico no es válido")

    else:
        try:
            conn = conectar()
            cursor = conn.cursor()

            # 🔎 Verificar si ya existían registros previos (solo para mensaje informativo)
            cursor.execute(
                "SELECT COUNT(*) FROM proveedores WHERE nit = %s",
                (nit,)
            )
            cantidad = cursor.fetchone()[0]

            # 🔥 SIEMPRE INSERTAMOS (guardamos histórico)
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
                st.success("Información actualizada correctamente. Se creó una nueva versión del registro.")
            else:
                st.success("Proveedor registrado correctamente.")

        except Exception as e:
            st.error(f"Error al guardar: {e}")

# =========================
# ZONA INTERNA COMPRAS
# =========================

st.markdown("---")
st.subheader("🔐 Zona interna - Compras")

if "auth" not in st.session_state:
    st.session_state.auth = False

password = st.text_input("Ingrese contraseña", type="password")

if password == os.getenv("ADMIN_PASSWORD"):
    st.session_state.auth = True

if st.session_state.auth:
    try:
        conn = conectar()

        # 🔥 SOLO TRAE EL ÚLTIMO REGISTRO POR NIT
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
        st.dataframe(df)

        # 📥 Descargar Excel
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

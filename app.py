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

# Inicializar estado para limpieza
if "reset" not in st.session_state:
    st.session_state.reset = False

if st.session_state.reset:
    st.session_state.nombre_empresa = ""
    st.session_state.nit = ""
    st.session_state.representante = ""
    st.session_state.numero_documento = ""
    st.session_state.correo = ""
    st.session_state.reset = False

nombre_empresa = st.text_input("Nombre de la empresa", key="nombre_empresa")
nit = st.text_input("NIT", key="nit")
representante = st.text_input("Nombre representante legal", key="representante")
tipo_documento = st.selectbox("Tipo documento", ["Cédula", "NIT", "Pasaporte"])
numero_documento = st.text_input("Número documento", key="numero_documento")
correo = st.text_input("Correo electrónico", key="correo")

col1, col2 = st.columns(2)

with col1:
    enviar = st.button("Enviar")

with col2:
    limpiar = st.button("Limpiar")

# =========================
# BOTÓN LIMPIAR
# =========================

if limpiar:
    st.session_state.reset = True
    st.rerun()

# =========================
# BOTÓN ENVIAR
# =========================

if enviar:

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

    elif not nit.isdigit():
        st.error("El NIT debe contener solo números")

    elif not numero_documento.isdigit():
        st.error("El número de documento debe contener solo números")

    elif not validar_email(correo):
        st.error("El correo electrónico no es válido")

    else:
        # 🔠 Normalización
        nombre_empresa = nombre_empresa.strip().upper()
        representante = representante.strip().upper()

        try:
            conn = conectar()
            cursor = conn.cursor()

            # Contar registros previos del mismo NIT
            cursor.execute(
                "SELECT COUNT(*) FROM proveedores WHERE nit = %s",
                (nit,)
            )
            cantidad = cursor.fetchone()[0]

            # 🔥 Siempre INSERT (histórico)
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
                st.success("Información actualizada correctamente. Se creó una nueva versión.")
            else:
                st.success("Proveedor registrado correctamente.")

            # 🔄 Limpieza automática
            st.session_state.reset = True
            st.rerun()

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

        # 🔥 SOLO ÚLTIMA VERSIÓN POR NIT
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

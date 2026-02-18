import streamlit as st
import psycopg2
import os
import pandas as pd

# 🔹 Conexión segura desde Secrets
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

# =========================
# FORMULARIO PROVEEDORES
# =========================

st.title("Formulario Proveedores")
st.write("Bienvenido al formulario de registro")

nombre = st.text_input("Nombre del proveedor")
empresa = st.text_input("Empresa")
correo = st.text_input("Correo electrónico")

if st.button("Enviar"):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO proveedores (nombre, empresa, correo) VALUES (%s, %s, %s)",
            (nombre, empresa, correo)
        )

        conn.commit()
        cursor.close()
        conn.close()

        st.success("Información enviada correctamente")

    except Exception as e:
        st.error(f"Error al guardar: {e}")

# =========================
# ZONA INTERNA COMPRAS
# =========================

st.markdown("---")
st.subheader("🔐 Zona interna - Compras")

password = st.text_input("Ingrese contraseña", type="password")

if password == os.getenv("ADMIN_PASSWORD"):

    try:
        conn = conectar()
        df = pd.read_sql("SELECT * FROM proveedores ORDER BY fecha_registro DESC", conn)
        conn.close()

        st.success("Acceso concedido")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Descargar base de datos",
            data=csv,
            file_name="proveedores.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error al consultar datos: {e}")

elif password != "":
    st.error("Contraseña incorrecta")

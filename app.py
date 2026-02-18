import streamlit as st
import psycopg2
import os

# 🔹 CONFIGURACIÓN SEGURA

DATABASE_URL = os.getenv("DATABASE_URL")



# 🔹 FUNCIÓN PARA CONECTAR
def conectar():
    return psycopg2.connect(DATABASE_URL)

# 🔹 INTERFAZ
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

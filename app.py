import streamlit as st
import psycopg2
import os
import pandas as pd
import re
from datetime import datetime

st.set_page_config(
    page_title="Portal Proveedores - GreenMovil",
    page_icon="🟢",
    layout="wide"
)

st.markdown("""
<style>
.block-container {padding-top: 2rem !important;}
h1 {font-size: 42px !important;font-weight:700 !important;}
h2 {font-size: 34px !important;font-weight:700 !important;}
h3 {font-size: 26px !important;font-weight:600 !important;}
label {font-size:18px !important;}
input {font-size:17px !important;text-transform:uppercase;}
.stButton>button {
background-color:#A1C42A;
color:white;
border-radius:8px;
padding:0.7em 1.6em;
}
.stButton>button:hover {background-color:#00594E;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='background-color:#A1C42A;height:4px;margin-bottom:20px;'></div>", unsafe_allow_html=True)

col_title,col_logo = st.columns([4,1])

with col_title:
    st.markdown("## Portal Oficial de Registro de Proveedores")
    st.markdown("""
Este portal permite el registro oficial de proveedores interesados en establecer relaciones comerciales con **GreenMóvil**  
La información suministrada será utilizada para procesos de validación y vinculación de proveedores.
""")
    st.markdown(f"<small>Fecha del sistema: {datetime.now().strftime('%d/%m/%Y')}</small>", unsafe_allow_html=True)

with col_logo:
    st.image("logo.png", use_container_width=True)

st.divider()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron,email)

tab1,tab2 = st.tabs(["📝 Registro Proveedor","🔐 Zona Compras"])

# =====================================================
# TAB 1
# =====================================================

with tab1:

    if "accionistas" not in st.session_state:
        st.session_state.accionistas=[]

    if "junta" not in st.session_state:
        st.session_state.junta=[]

    if "mensaje_ok" not in st.session_state:
        st.session_state.mensaje_ok=False

    if st.session_state.mensaje_ok:
        st.success("La información fue registrada correctamente.")
        st.session_state.mensaje_ok=False

    with st.form("form_proveedor", clear_on_submit=True):

        st.subheader("🏢 Información de la empresa")

        col1,col2,col3=st.columns([3,2,1])

        with col1:
            nombre_empresa=st.text_input("Nombre empresa")

        with col2:
            nit=st.text_input("NIT")

        with col3:
            dv=st.text_input("DV",max_chars=1)

        correo=st.text_input("Correo electrónico")

        st.divider()

        st.subheader("👤 Representante legal")

        col1,col2=st.columns(2)

        with col1:
            nombre=st.text_input("Nombre representante")
            tipo_documento=st.selectbox("Tipo documento",["CC","CE","NIT","Pasaporte"])

        with col2:
            cargo=st.selectbox("Cargo",["Representante Legal"])
            numero_documento=st.text_input("Número documento")

        st.divider()
        st.subheader("📊 Accionistas")

        for i in range(len(st.session_state.accionistas)):

            col1,col2,col3,col4=st.columns([3,2,2,1])

            with col1:
                st.text_input("Nombre",key=f"acc_nombre_{i}")

            with col2:
                st.selectbox("Tipo",["CC","CE","Pasaporte"],key=f"acc_tipo_{i}")

            with col3:
                st.text_input("Documento",key=f"acc_doc_{i}")

            with col4:
                if st.form_submit_button("❌",key=f"del_acc_{i}"):
                    st.session_state.accionistas.pop(i)
                    st.rerun()

        if st.form_submit_button("➕ Agregar accionista"):
            st.session_state.accionistas.append({})
            st.rerun()

        st.divider()
        st.subheader("🏛 Junta directiva")

        for i in range(len(st.session_state.junta)):

            col1,col2,col3,col4=st.columns([3,2,2,1])

            with col1:
                st.text_input("Nombre",key=f"jd_nombre_{i}")

            with col2:
                st.selectbox("Tipo",["CC","CE","Pasaporte"],key=f"jd_tipo_{i}")

            with col3:
                st.text_input("Documento",key=f"jd_doc_{i}")

            with col4:
                if st.form_submit_button("❌",key=f"del_jd_{i}"):
                    st.session_state.junta.pop(i)
                    st.rerun()

        if st.form_submit_button("➕ Agregar miembro junta"):
            st.session_state.junta.append({})
            st.rerun()

        col1,col2=st.columns(2)

        registrar=col1.form_submit_button("Registrar información")
        borrar=col2.form_submit_button("🗑️ Borrar formulario")

        if borrar:
            st.session_state.accionistas=[]
            st.session_state.junta=[]
            st.rerun()

        if registrar:

            if not nombre_empresa.strip():
                st.error("Debe ingresar empresa")

            elif not nit.isdigit() or len(nit)!=9:
                st.error("El NIT debe tener exactamente 9 números.")

            elif not dv.isdigit():
                st.error("El DV debe contener solo números.")

            elif not numero_documento.isdigit():
                st.error("El número de documento debe contener solo números.")

            elif not validar_email(correo):
                st.error("Correo inválido")

            else:

                try:

                    conn=conectar()
                    cursor=conn.cursor()

                    cursor.execute("""
                    INSERT INTO proveedores
                    (nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,(nombre_empresa,nit,dv,tipo_documento,numero_documento,nombre,cargo,correo))

                    conn.commit()
                    conn.close()

                    st.session_state.mensaje_ok=True
                    st.session_state.accionistas=[]
                    st.session_state.junta=[]

                    st.rerun()

                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.subheader("Base de proveedores registrados")

    ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","Compras2026")

    password=st.text_input("Ingrese contraseña",type="password")

    if password==ADMIN_PASSWORD:

        conn=conectar()

        df=pd.read_sql("""
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
        """,conn)

        conn.close()

        st.dataframe(df,use_container_width=True)

        csv=df.to_csv(index=False).encode("utf-8")

        st.download_button(
        label="📥 Descargar base de proveedores",
        data=csv,
        file_name="base_proveedores.csv",
        mime="text/csv"
        )

    elif password!="":
        st.error("Contraseña incorrecta")
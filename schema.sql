DROP TABLE IF EXISTS proveedores;

CREATE TABLE proveedores (

    id SERIAL PRIMARY KEY,

    nombre_empresa TEXT NOT NULL,

    nit TEXT NOT NULL,

    dv TEXT NOT NULL,

    tipo_documento TEXT NOT NULL,

    numero_documento TEXT NOT NULL,

    nombre TEXT NOT NULL,

    cargo TEXT NOT NULL,

    correo TEXT,

    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE proveedores
ADD CONSTRAINT unique_persona_empresa
UNIQUE (nit, numero_documento, cargo);
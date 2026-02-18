DROP TABLE IF EXISTS proveedores;

CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre_empresa TEXT NOT NULL,
    nit TEXT NOT NULL,a
    representante_legal TEXT NOT NULL,
    tipo_documento TEXT NOT NULL,
    numero_documento TEXT NOT NULL,
    correo TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

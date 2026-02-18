CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200),
    empresa VARCHAR(200),
    correo VARCHAR(200),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

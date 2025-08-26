
USE GestionDatos;
GO

-- Tabla de Estatus de Cliente
CREATE TABLE ESTATUS_CLIENTE (
    estatus_cliente_id INT PRIMARY KEY,
    nombre_estatus VARCHAR(100) NOT NULL
);

-- Tabla de Género
CREATE TABLE GENERO (
    genero_id INT PRIMARY KEY,
    nombre_genero VARCHAR(50) NOT NULL
);

-- Tabla de Dirección
CREATE TABLE DIRECCION (
    direccion_id INT IDENTITY(1,1) PRIMARY KEY,
    calle VARCHAR(50) NOT NULL,
    numero_interior INT NULL,
    numero_exterior INT NOT NULL,
    ciudad VARCHAR(50) NOT NULL,
    estado VARCHAR(50) NOT NULL,
    codigo_postal VARCHAR(10) NOT NULL
);

-- Tabla de Cliente
CREATE TABLE CLIENTE (
    cliente_id INT IDENTITY(1,1) PRIMARY KEY,
    primer_nombre VARCHAR(90) NOT NULL,
    segundo_nombre VARCHAR(90) NULL,
    primer_apellido VARCHAR(100) NOT NULL,
    segundo_apellido VARCHAR(100) NOT NULL,
    nacionalidad VARCHAR(80) NULL,
    ocupacion VARCHAR(100) NULL,
    estatus_cliente_id INT NOT NULL,
    genero_id INT NOT NULL,
    telefono VARCHAR(25) NOT NULL,
    email VARCHAR(100) NOT NULL,
    direccion_id INT NULL,
    fecha_nacimiento DATE NOT NULL,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    CONSTRAINT UQ_cliente_email UNIQUE (email),
    CONSTRAINT FK_cliente_estatus FOREIGN KEY (estatus_cliente_id) REFERENCES ESTATUS_CLIENTE(estatus_cliente_id),
    CONSTRAINT FK_cliente_genero FOREIGN KEY (genero_id) REFERENCES GENERO(genero_id),
    CONSTRAINT FK_cliente_direccion FOREIGN KEY (direccion_id) REFERENCES DIRECCION(direccion_id),
    CONSTRAINT CHK_Email_Format CHECK (email LIKE '%_@_%._%')
);

-- Tabla de Estatus de Cuenta
CREATE TABLE ESTATUS_CUENTA (
    estatus_cuenta_id INT PRIMARY KEY,
    estatus_cuenta VARCHAR(50) NOT NULL
);

-- Tabla de Cuenta (corregida la relación 1:1 a 1:N)
CREATE TABLE CUENTA (
    cuenta_id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_creacion DATE NOT NULL,
    saldo_inicial DECIMAL(19,4) NOT NULL,
    saldo DECIMAL(19,4) NOT NULL,
    estatus_cuenta_id INT NOT NULL,
    cliente_id INT NOT NULL,
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_cuenta_estatus FOREIGN KEY (estatus_cuenta_id) REFERENCES ESTATUS_CUENTA(estatus_cuenta_id),
    CONSTRAINT FK_cuenta_cliente FOREIGN KEY (cliente_id) REFERENCES CLIENTE(cliente_id),
    CONSTRAINT CHK_Saldo_Positivo CHECK (saldo >= 0),
    CONSTRAINT CHK_Saldo_Inicial_Positivo CHECK (saldo_inicial >= 0)
);

-- Tabla de Tipo de Transacción
CREATE TABLE TIPO_TRANSACCION (
    transaccion_id INT PRIMARY KEY,
    tipo_transaccion VARCHAR(50) NOT NULL,
    tipo_operacion VARCHAR(50) NOT NULL
);

-- Tabla de Movimiento
CREATE TABLE MOVIMIENTO (
    movimiento_id INT IDENTITY(1,1) PRIMARY KEY,
    cantidad DECIMAL(19,4) NOT NULL,
    fecha_transaccion DATE NOT NULL,
    cuenta_id INT NOT NULL,
    transaccion_id INT NOT NULL,
    CONSTRAINT FK_movimiento_cuenta FOREIGN KEY (cuenta_id) REFERENCES CUENTA(cuenta_id),
    CONSTRAINT FK_movimiento_transaccion FOREIGN KEY (transaccion_id) REFERENCES TIPO_TRANSACCION(transaccion_id)
);

-- Creación de índices para mejorar el rendimiento
CREATE INDEX IX_MOVIMIENTO_FECHA ON MOVIMIENTO(fecha_transaccion);
CREATE INDEX IX_CUENTA_FECHA_CREACION ON CUENTA(fecha_creacion);
CREATE INDEX IX_CUENTA_CLIENTE ON CUENTA(cliente_id);
CREATE INDEX IX_CLIENTE_EMAIL ON CLIENTE(email);
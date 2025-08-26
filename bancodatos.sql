
-- Tabla: Direcciones
-- Almacena la información de las direcciones de los clientes.
CREATE TABLE Direcciones (
    ID_Direccion INT PRIMARY KEY,
    Calle VARCHAR(255),
    Numero VARCHAR(50),
    Ciudad VARCHAR(100),
    Estado VARCHAR(100),
    CodigoPostal VARCHAR(20),
    Pais VARCHAR(100)
);

-- Tabla: Clientes
-- Guarda los datos personales de los clientes y establece la relación con la dirección.
CREATE TABLE Clientes (
    ID_Cliente INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellido VARCHAR(100),
    Telefono VARCHAR(50),
    ID_Direccion INT,
    FOREIGN KEY (ID_Direccion) REFERENCES Direcciones(ID_Direccion)
);

-- Tabla: TiposCuenta
-- Define los tipos de cuentas disponibles, como 'Ahorros' o 'Corriente'.
CREATE TABLE TiposCuenta (
    ID_TipoCuenta INT PRIMARY KEY,
    Nombre_Tipo VARCHAR(50),
    Descripcion VARCHAR(255),
    Tasa_Interes FLOAT
);

-- Tabla: Cuentas
-- Contiene las cuentas bancarias de los clientes, vinculadas a un cliente y a un tipo de cuenta.
CREATE TABLE Cuentas (
    Numero_Cuenta INT PRIMARY KEY,
    Saldo DECIMAL(10, 2),
    Fecha_Creacion DATE,
    ID_Cliente INT,
    ID_TipoCuenta INT,
    FOREIGN KEY (ID_Cliente) REFERENCES Clientes(ID_Cliente),
    FOREIGN KEY (ID_TipoCuenta) REFERENCES TiposCuenta(ID_TipoCuenta)
);

-- Tabla: Movimientos
-- Registra cada transacción o movimiento realizado en una cuenta específica.
CREATE TABLE Movimientos (
    ID_Movimiento INT PRIMARY KEY,
    Fecha DATE,
    Tipo VARCHAR(50),
    Monto DECIMAL(10, 2),
    Numero_Cuenta INT,
    FOREIGN KEY (Numero_Cuenta) REFERENCES Cuentas(Numero_Cuenta)
);


-- ######################################################################
-- #                     INSERCIÓN DE DATOS                             #
-- ######################################################################

-- Insertar datos en la tabla Direcciones
INSERT INTO Direcciones (ID_Direccion, Calle, Numero, Ciudad, Estado, CodigoPostal, Pais) VALUES
(1, 'Avenida Principal', '123', 'Madrid', 'Comunidad de Madrid', '28001', 'España'),
(2, 'Calle Falsa', '45', 'Barcelona', 'Cataluña', '08001', 'España'),
(3, 'Paseo de la Castellana', '789', 'Madrid', 'Comunidad de Madrid', '28046', 'España'),
(4, 'Gran Vía', '10', 'Madrid', 'Comunidad de Madrid', '28013', 'España'),
(5, 'Calle del Sol', '22', 'Valencia', 'Comunidad Valenciana', '46001', 'España');

-- Insertar datos en la tabla Clientes
INSERT INTO Clientes (ID_Cliente, Nombre, Apellido, Telefono, ID_Direccion) VALUES
(101, 'Ana', 'García', '601-123-456', 1),
(102, 'Luis', 'Pérez', '602-987-654', 2),
(103, 'Sofía', 'Martínez', '603-111-222', 3),
(104, 'Carlos', 'López', '604-333-444', 4),
(105, 'María', 'Hernández', '605-555-666', 5);

-- Insertar datos en la tabla TiposCuenta
INSERT INTO TiposCuenta (ID_TipoCuenta, Nombre_Tipo, Descripcion, Tasa_Interes) VALUES
(1, 'Ahorros', 'Cuenta para ahorrar dinero con intereses.', 1.5),
(2, 'Corriente', 'Cuenta para transacciones diarias sin intereses.', 0.25),
(3, 'Inversión', 'Cuenta para inversiones de alto rendimiento.', 3.0);

-- Insertar datos en la tabla Cuentas
INSERT INTO Cuentas (Numero_Cuenta, Saldo, Fecha_Creacion, ID_Cliente, ID_TipoCuenta) VALUES
(1001, 5000.50, '2022-01-15', 101, 1),
(1002, 1200.00, '2022-02-20', 102, 2),
(1003, 15000.75, '2022-03-10', 103, 3),
(1004, 300.00, '2022-04-05', 104, 2),
(1005, 8000.25, '2022-05-30', 105, 1);

-- Insertar datos en la tabla Movimientos
INSERT INTO Movimientos (ID_Movimiento, Fecha, Tipo, Monto, Numero_Cuenta) VALUES
(2001, '2023-01-20', 'Depósito', 200.00, 1001),
(2002, '2023-01-25', 'Retiro', 50.00, 1002),
(2003, '2023-02-01', 'Transferencia', 1000.00, 1003),
(2004, '2023-02-05', 'Depósito', 50.00, 1004),
(2005, '2023-02-10', 'Retiro', 250.00, 1005);
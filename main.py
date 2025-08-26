from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional
import pyodbc

# Configuración de la base de datos (¡ACTUALIZA CON TUS CREDENCIALES!)
DATABASE_URL = "mssql+pyodbc://usuario:contraseña@servidor/GestionDatos?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de SQLAlchemy (reflejan exactamente tus tablas)
class EstatusClienteDB(Base):
    __tablename__ = "ESTATUS_CLIENTE"
    estatus_cliente_id = Column(Integer, primary_key=True)
    nombre_estatus = Column(String(100), nullable=False)

class GeneroDB(Base):
    __tablename__ = "GENERO"
    genero_id = Column(Integer, primary_key=True)
    nombre_genero = Column(String(50), nullable=False)

class DireccionDB(Base):
    __tablename__ = "DIRECCION"
    direccion_id = Column(Integer, primary_key=True, autoincrement=True)
    calle = Column(String(50), nullable=False)
    numero_interior = Column(Integer, nullable=True)
    numero_exterior = Column(Integer, nullable=False)
    ciudad = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    codigo_postal = Column(String(10), nullable=False)
    clientes = relationship("ClienteDB", back_populates="direccion")

class ClienteDB(Base):
    __tablename__ = "CLIENTE"
    cliente_id = Column(Integer, primary_key=True, autoincrement=True)
    primer_nombre = Column(String(90), nullable=False)
    segundo_nombre = Column(String(90), nullable=True)
    primer_apellido = Column(String(100), nullable=False)
    segundo_apellido = Column(String(100), nullable=False)
    nacionalidad = Column(String(80), nullable=True)
    ocupacion = Column(String(100), nullable=True)
    estatus_cliente_id = Column(Integer, ForeignKey("ESTATUS_CLIENTE.estatus_cliente_id"), nullable=False)
    genero_id = Column(Integer, ForeignKey("GENERO.genero_id"), nullable=False)
    telefono = Column(String(25), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    direccion_id = Column(Integer, ForeignKey("DIRECCION.direccion_id"), nullable=True)
    fecha_nacimiento = Column(Date, nullable=False)
    
    estatus = relationship("EstatusClienteDB")
    genero = relationship("GeneroDB")
    direccion = relationship("DireccionDB", back_populates="clientes")
    cuenta = relationship("CuentaDB", uselist=False, back_populates="cliente")

class EstatusCuentaDB(Base):
    __tablename__ = "ESTATUS_CUENTA"
    estatus_cuenta_id = Column(Integer, primary_key=True)
    estatus_cuenta = Column(String(50), nullable=False)

class CuentaDB(Base):
    __tablename__ = "CUENTA"
    cuenta_id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(Date, nullable=False)
    saldo_inicial = Column(DECIMAL(18, 2), nullable=False)
    saldo = Column(DECIMAL(18, 2), nullable=False)
    estatus_cuenta_id = Column(Integer, ForeignKey("ESTATUS_CUENTA.estatus_cuenta_id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("CLIENTE.cliente_id"), nullable=False, unique=True)
    
    estatus = relationship("EstatusCuentaDB")
    cliente = relationship("ClienteDB", back_populates="cuenta")
    movimientos = relationship("MovimientoDB", back_populates="cuenta")

class TipoTransaccionDB(Base):
    __tablename__ = "TIPO_TRANSACCION"
    transaccion_id = Column(Integer, primary_key=True)
    tipo_transaccion = Column(String(50), nullable=False)
    tipo_operacion = Column(String(50), nullable=False)

class MovimientoDB(Base):
    __tablename__ = "MOVIMIENTO"
    movimiento_id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(DECIMAL(18, 2), nullable=False)
    fecha_transaccion = Column(Date, nullable=False)
    cuenta_id = Column(Integer, ForeignKey("CUENTA.cuenta_id"), nullable=False)
    transaccion_id = Column(Integer, ForeignKey("TIPO_TRANSACCION.transaccion_id"), nullable=False)
    
    cuenta = relationship("CuentaDB", back_populates="movimientos")
    tipo_transaccion = relationship("TipoTransaccionDB")

Base.metadata.create_all(bind=engine)

# Modelos Pydantic para request/response
class DireccionCreate(BaseModel):
    calle: str
    numero_interior: Optional[int] = None
    numero_exterior: int
    ciudad: str
    estado: str
    codigo_postal: str

class DireccionResponse(DireccionCreate):
    direccion_id: int
    
    class Config:
        orm_mode = True

class ClienteCreate(BaseModel):
    primer_nombre: str
    segundo_nombre: Optional[str] = None
    primer_apellido: str
    segundo_apellido: str
    nacionalidad: Optional[str] = None
    ocupacion: Optional[str] = None
    estatus_cliente_id: int
    genero_id: int
    telefono: str
    email: str
    direccion_id: Optional[int] = None
    fecha_nacimiento: date

class ClienteResponse(ClienteCreate):
    cliente_id: int
    
    class Config:
        orm_mode = True

class CuentaCreate(BaseModel):
    fecha_creacion: date
    saldo_inicial: float
    saldo: float
    estatus_cuenta_id: int
    cliente_id: int

class CuentaResponse(CuentaCreate):
    cuenta_id: int
    
    class Config:
        orm_mode = True

class MovimientoCreate(BaseModel):
    cantidad: float
    fecha_transaccion: date
    cuenta_id: int
    transaccion_id: int

class MovimientoResponse(MovimientoCreate):
    movimiento_id: int
    
    class Config:
        orm_mode = True

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Sistema Bancario API", version="1.0")

# CRUD para Direcciones
@app.post("/direcciones/", response_model=DireccionResponse)
def crear_direccion(direccion: DireccionCreate, db: Session = Depends(get_db)):
    db_direccion = DireccionDB(**direccion.dict())
    db.add(db_direccion)
    db.commit()
    db.refresh(db_direccion)
    return db_direccion

@app.get("/direcciones/", response_model=List[DireccionResponse])
def leer_direcciones(db: Session = Depends(get_db)):
    return db.query(DireccionDB).all()

# CRUD para Clientes
@app.post("/clientes/", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    if db.query(ClienteDB).filter(ClienteDB.email == cliente.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    db_cliente = ClienteDB(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/clientes/", response_model=List[ClienteResponse])
def leer_clientes(db: Session = Depends(get_db)):
    return db.query(ClienteDB).all()

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def leer_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# CRUD para Cuentas
@app.post("/cuentas/", response_model=CuentaResponse)
def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_db)):
    # Verificar si el cliente ya tiene cuenta (relación 1:1)
    if db.query(CuentaDB).filter(CuentaDB.cliente_id == cuenta.cliente_id).first():
        raise HTTPException(status_code=400, detail="El cliente ya tiene una cuenta")
    
    db_cuenta = CuentaDB(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

@app.get("/cuentas/", response_model=List[CuentaResponse])
def leer_cuentas(db: Session = Depends(get_db)):
    return db.query(CuentaDB).all()

@app.get("/cuentas/{cuenta_id}", response_model=CuentaResponse)
def leer_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.query(CuentaDB).filter(CuentaDB.cuenta_id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

# Operaciones bancarias
@app.post("/movimientos/", response_model=MovimientoResponse)
def crear_movimiento(movimiento: MovimientoCreate, db: Session = Depends(get_db)):
    # Verificar si la cuenta existe
    cuenta = db.query(CuentaDB).filter(CuentaDB.cuenta_id == movimiento.cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    # Verificar el tipo de transacción
    transaccion = db.query(TipoTransaccionDB).filter(
        TipoTransaccionDB.transaccion_id == movimiento.transaccion_id
    ).first()
    if not transaccion:
        raise HTTPException(status_code=404, detail="Tipo de transacción no válido")
    
    # Actualizar saldo según el tipo de operación
    if transaccion.tipo_operacion.lower() == "retiro":
        if cuenta.saldo < movimiento.cantidad:
            raise HTTPException(status_code=400, detail="Fondos insuficientes")
        cuenta.saldo -= movimiento.cantidad
    elif transaccion.tipo_operacion.lower() == "deposito":
        cuenta.saldo += movimiento.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de operación no válido")
    
    db_movimiento = MovimientoDB(**movimiento.dict())
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

@app.get("/cuentas/{cuenta_id}/movimientos", response_model=List[MovimientoResponse])
def obtener_movimientos_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    return db.query(MovimientoDB).filter(MovimientoDB.cuenta_id == cuenta_id).all()

# Consultas adicionales útiles
@app.get("/clientes/{cliente_id}/cuenta")
def obtener_cuenta_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cuenta = db.query(CuentaDB).filter(CuentaDB.cliente_id == cliente_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="El cliente no tiene cuenta")
    return cuenta

@app.get("/cuentas/{cuenta_id}/saldo")
def consultar_saldo(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.query(CuentaDB).filter(CuentaDB.cuenta_id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return {"saldo_actual": cuenta.saldo}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
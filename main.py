from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, DECIMAL, CheckConstraint, event
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import List, Optional
import re
import pyodbc

# Configuración de la base de datos (ACTUALIZA CON TUS CREDENCIALES)
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
    fecha_creacion = Column(DateTime, default=func.now())
    
    estatus = relationship("EstatusClienteDB")
    genero = relationship("GeneroDB")
    direccion = relationship("DireccionDB", back_populates="clientes")
    cuentas = relationship("CuentaDB", back_populates="cliente")
    
    __table_args__ = (
        CheckConstraint('email LIKE "%_@_%._%"', name='CHK_Email_Format'),
    )

class EstatusCuentaDB(Base):
    __tablename__ = "ESTATUS_CUENTA"
    estatus_cuenta_id = Column(Integer, primary_key=True)
    estatus_cuenta = Column(String(50), nullable=False)

class CuentaDB(Base):
    __tablename__ = "CUENTA"
    cuenta_id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(Date, nullable=False)
    saldo_inicial = Column(DECIMAL(19, 4), nullable=False)
    saldo = Column(DECIMAL(19, 4), nullable=False)
    estatus_cuenta_id = Column(Integer, ForeignKey("ESTATUS_CUENTA.estatus_cuenta_id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("CLIENTE.cliente_id"), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    estatus = relationship("EstatusCuentaDB")
    cliente = relationship("ClienteDB", back_populates="cuentas")
    movimientos = relationship("MovimientoDB", back_populates="cuenta")
    
    __table_args__ = (
        CheckConstraint('saldo >= 0', name='CHK_Saldo_Positivo'),
        CheckConstraint('saldo_inicial >= 0', name='CHK_Saldo_Inicial_Positivo'),
    )

class TipoTransaccionDB(Base):
    __tablename__ = "TIPO_TRANSACCION"
    transaccion_id = Column(Integer, primary_key=True)
    tipo_transaccion = Column(String(50), nullable=False)
    tipo_operacion = Column(String(50), nullable=False)

class MovimientoDB(Base):
    __tablename__ = "MOVIMIENTO"
    movimiento_id = Column(Integer, primary_key=True, autoincrement=True)
    cantidad = Column(DECIMAL(19, 4), nullable=False)
    fecha_transaccion = Column(Date, nullable=False)
    cuenta_id = Column(Integer, ForeignKey("CUENTA.cuenta_id"), nullable=False)
    transaccion_id = Column(Integer, ForeignKey("TIPO_TRANSACCION.transaccion_id"), nullable=False)
    
    cuenta = relationship("CuentaDB", back_populates="movimientos")
    tipo_transaccion = relationship("TipoTransaccionDB")

Base.metadata.create_all(bind=engine)

# Modelos Pydantic para request/response
class DireccionBase(BaseModel):
    calle: str
    numero_interior: Optional[int] = None
    numero_exterior: int
    ciudad: str
    estado: str
    codigo_postal: str

class DireccionCreate(DireccionBase):
    pass

class DireccionResponse(DireccionBase):
    direccion_id: int
    
    class Config:
        orm_mode = True

class ClienteBase(BaseModel):
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

    @validator('email')
    def validate_email_format(cls, v):
        if not re.match(r'[^@]+@[^@]+\.[^@]+', v):
            raise ValueError('Formato de email inválido')
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    cliente_id: int
    fecha_creacion: datetime
    
    class Config:
        orm_mode = True

class CuentaBase(BaseModel):
    fecha_creacion: date
    saldo_inicial: float
    saldo: float
    estatus_cuenta_id: int
    cliente_id: int

    @validator('saldo_inicial', 'saldo')
    def validate_positive_values(cls, v):
        if v < 0:
            raise ValueError('El valor debe ser positivo')
        return v

class CuentaCreate(CuentaBase):
    pass

class CuentaResponse(CuentaBase):
    cuenta_id: int
    fecha_actualizacion: datetime
    
    class Config:
        orm_mode = True

class MovimientoBase(BaseModel):
    cantidad: float
    fecha_transaccion: date
    cuenta_id: int
    transaccion_id: int

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoResponse(MovimientoBase):
    movimiento_id: int
    
    class Config:
        orm_mode = True

class TransaccionInfo(BaseModel):
    transaccion_id: int
    tipo_transaccion: str
    tipo_operacion: str
    
    class Config:
        orm_mode = True

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Sistema Bancario API",
    description="API completa para gestión de sistema bancario",
    version="2.0"
)

# CRUD para Direcciones
@app.post("/direcciones/", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
def crear_direccion(direccion: DireccionCreate, db: Session = Depends(get_db)):
    db_direccion = DireccionDB(**direccion.dict())
    db.add(db_direccion)
    db.commit()
    db.refresh(db_direccion)
    return db_direccion

@app.get("/direcciones/", response_model=List[DireccionResponse])
def leer_direcciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DireccionDB).offset(skip).limit(limit).all()

@app.get("/direcciones/{direccion_id}", response_model=DireccionResponse)
def leer_direccion(direccion_id: int, db: Session = Depends(get_db)):
    direccion = db.query(DireccionDB).filter(DireccionDB.direccion_id == direccion_id).first()
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion

# CRUD para Clientes
@app.post("/clientes/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    if db.query(ClienteDB).filter(ClienteDB.email == cliente.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Verificar que existan las referencias
    if not db.query(EstatusClienteDB).filter(EstatusClienteDB.estatus_cliente_id == cliente.estatus_cliente_id).first():
        raise HTTPException(status_code=400, detail="Estatus de cliente no válido")
    
    if not db.query(GeneroDB).filter(GeneroDB.genero_id == cliente.genero_id).first():
        raise HTTPException(status_code=400, detail="Género no válido")
    
    if cliente.direccion_id and not db.query(DireccionDB).filter(DireccionDB.direccion_id == cliente.direccion_id).first():
        raise HTTPException(status_code=400, detail="Dirección no válida")
    
    db_cliente = ClienteDB(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/clientes/", response_model=List[ClienteResponse])
def leer_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ClienteDB).offset(skip).limit(limit).all()

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def leer_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.get("/clientes/email/{email}", response_model=ClienteResponse)
def buscar_cliente_por_email(email: str, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.email == email).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# CRUD para Cuentas
@app.post("/cuentas/", response_model=CuentaResponse, status_code=status.HTTP_201_CREATED)
def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_db)):
    # Verificar que el cliente existe
    cliente = db.query(ClienteDB).filter(ClienteDB.cliente_id == cuenta.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Verificar que el estatus de cuenta existe
    if not db.query(EstatusCuentaDB).filter(EstatusCuentaDB.estatus_cuenta_id == cuenta.estatus_cuenta_id).first():
        raise HTTPException(status_code=400, detail="Estatus de cuenta no válido")
    
    # Verificar que el saldo inicial sea igual al saldo
    if cuenta.saldo_inicial != cuenta.saldo:
        raise HTTPException(status_code=400, detail="El saldo inicial debe ser igual al saldo actual")
    
    db_cuenta = CuentaDB(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta

@app.get("/cuentas/", response_model=List[CuentaResponse])
def leer_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(CuentaDB).offset(skip).limit(limit).all()

@app.get("/cuentas/{cuenta_id}", response_model=CuentaResponse)
def leer_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.query(CuentaDB).filter(CuentaDB.cuenta_id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

@app.get("/clientes/{cliente_id}/cuentas", response_model=List[CuentaResponse])
def obtener_cuentas_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(CuentaDB).filter(CuentaDB.cliente_id == cliente_id).all()

# Operaciones bancarias
@app.post("/movimientos/", response_model=MovimientoResponse, status_code=status.HTTP_201_CREATED)
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
    
    # Validar cantidad positiva
    if movimiento.cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser positiva")
    
    # Actualizar saldo según el tipo de operación
    if transaccion.tipo_operacion.lower() == "retiro":
        if cuenta.saldo < movimiento.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Fondos insuficientes. Saldo actual: {cuenta.saldo}"
            )
        cuenta.saldo -= movimiento.cantidad
    elif transaccion.tipo_operacion.lower() == "deposito":
        cuenta.saldo += movimiento.cantidad
    else:
        raise HTTPException(status_code=400, detail="Tipo de operación no válido")
    
    db_movimiento = MovimientoDB(**movimiento.dict())
    db.add(db_movimiento)
    db.commit()
    db.refresh(db_movimiento)
    
    # Actualizar fecha de actualización de la cuenta
    cuenta.fecha_actualizacion = func.now()
    db.commit()
    
    return db_movimiento

@app.get("/movimientos/", response_model=List[MovimientoResponse])
def leer_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(MovimientoDB).offset(skip).limit(limit).all()

@app.get("/cuentas/{cuenta_id}/movimientos", response_model=List[MovimientoResponse])
def obtener_movimientos_cuenta(cuenta_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(MovimientoDB).filter(
        MovimientoDB.cuenta_id == cuenta_id
    ).offset(skip).limit(limit).all()

@app.get("/transacciones/", response_model=List[TransaccionInfo])
def obtener_tipos_transaccion(db: Session = Depends(get_db)):
    return db.query(TipoTransaccionDB).all()

# Consultas adicionales útiles
@app.get("/cuentas/{cuenta_id}/saldo")
def consultar_saldo(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.query(CuentaDB).filter(CuentaDB.cuenta_id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return {
        "cuenta_id": cuenta_id,
        "saldo_actual": float(cuenta.saldo),
        "moneda": "MXN",
        "fecha_consulta": datetime.now()
    }

@app.get("/clientes/{cliente_id}/resumen")
def resumen_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteDB).filter(ClienteDB.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cuentas = db.query(CuentaDB).filter(CuentaDB.cliente_id == cliente_id).all()
    total_saldo = sum(float(cuenta.saldo) for cuenta in cuentas)
    
    return {
        "cliente_id": cliente_id,
        "nombre_completo": f"{cliente.primer_nombre} {cliente.primer_apellido}",
        "total_cuentas": len(cuentas),
        "saldo_total": total_saldo,
        "cuentas": [
            {
                "cuenta_id": cuenta.cuenta_id,
                "saldo": float(cuenta.saldo),
                "estatus": cuenta.estatus.estatus_cuenta
            } for cuenta in cuentas
        ]
    }

# Endpoints para datos maestros
@app.get("/estatus-clientes/")
def obtener_estatus_clientes(db: Session = Depends(get_db)):
    return db.query(EstatusClienteDB).all()

@app.get("/generos/")
def obtener_generos(db: Session = Depends(get_db)):
    return db.query(GeneroDB).all()

@app.get("/estatus-cuentas/")
def obtener_estatus_cuentas(db: Session = Depends(get_db)):
    return db.query(EstatusCuentaDB).all()

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
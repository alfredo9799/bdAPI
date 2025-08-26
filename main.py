from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Configura la conexión a la base de datos
connection_string = (
    "mssql+pyodbc://usuario:contraseña@servidor/nombre_base_datos?driver=SQL+Server"
)
engine = create_engine(connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define tu modelo de base de datos (ejemplo: tabla Cuentas)
class CuentaDB(Base):
    __tablename__ = "cuentas"
    id = Column(Integer, primary_key=True, index=True)
    titular = Column(String, index=True)
    saldo = Column(Float)

# Crea las tablas (si no existen)
Base.metadata.create_all(bind=engine)

# Modelo Pydantic para la API
class Cuenta(BaseModel):
    id: int
    titular: str
    saldo: float

    class Config:
        orm_mode = True

# Inicia la app de FastAPI
app = FastAPI()

# CREATE - Agregar nueva cuenta
@app.post("/cuentas/")
def crear_cuenta(cuenta: Cuenta):
    db = SessionLocal()
    db_cuenta = CuentaDB(**cuenta.dict())
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    db.close()
    return db_cuenta

# READ - Obtener cuenta por ID
@app.get("/cuentas/{cuenta_id}")
def leer_cuenta(cuenta_id: int):
    db = SessionLocal()
    cuenta = db.query(CuentaDB).filter(CuentaDB.id == cuenta_id).first()
    db.close()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

# UPDATE - Actualizar cuenta
@app.put("/cuentas/{cuenta_id}")
def actualizar_cuenta(cuenta_id: int, cuenta: Cuenta):
    db = SessionLocal()
    db_cuenta = db.query(CuentaDB).filter(CuentaDB.id == cuenta_id).first()
    if db_cuenta is None:
        db.close()
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    db_cuenta.titular = cuenta.titular
    db_cuenta.saldo = cuenta.saldo
    db.commit()
    db.refresh(db_cuenta)
    db.close()
    return db_cuenta

# DELETE - Eliminar cuenta
@app.delete("/cuentas/{cuenta_id}")
def eliminar_cuenta(cuenta_id: int):
    db = SessionLocal()
    db_cuenta = db.query(CuentaDB).filter(CuentaDB.id == cuenta_id).first()
    if db_cuenta is None:
        db.close()
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    db.delete(db_cuenta)
    db.commit()
    db.close()
    return {"mensaje": "Cuenta eliminada"}
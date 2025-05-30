from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

app = FastAPI()
UPLOAD_DIR = "media/imagenes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL config (igual que Django)
DATABASE_URL = "postgresql+psycopg2://azurlitos:azurlitos@10.5.192.3:5432/pacientes_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ImagenMedica(Base):
    __tablename__ = "imagen_imagenmedica"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    archivo = Column(String)
    fecha_carga = Column(DateTime, default=datetime.utcnow)
    paciente_id = Column(Integer, ForeignKey("pacientes_paciente.id"))
    vista_axial = Column(String, nullable=True)
    vista_sagital = Column(String, nullable=True)
    vista_coronal = Column(String, nullable=True)

@app.post("/imagen/upload/")
async def upload_image(file: UploadFile = File(...), paciente_id: str = Form(...)):
    # Solo guarda el registro en la base de datos, no guarda el archivo
    db = SessionLocal()
    try:
        imagen_db = ImagenMedica(
            nombre=file.filename,
            archivo=file.filename,  # Solo el nombre, no la ruta
            fecha_carga=datetime.utcnow(),
            paciente_id=int(paciente_id),
            vista_axial=None,
            vista_sagital=None,
            vista_coronal=None
        )
        db.add(imagen_db)
        db.commit()
        db.refresh(imagen_db)
    finally:
        db.close()
    return {"filename": file.filename, "paciente_id": paciente_id, "msg": "Imagen registrada en la base de datos (no guardada en disco)"}

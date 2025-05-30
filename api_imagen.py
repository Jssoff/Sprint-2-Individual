from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
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

@app.get("/imagen/view/{filename}")
def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file_path)

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
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

@app.get("/imagen/cargar/", response_class=HTMLResponse)
async def cargar_imagen_form():
    # Formulario HTML simple para cargar imagen
    return '''
    <html><head><title>Cargar Imagen</title></head><body>
    <h1>Cargar Imagen Médica</h1>
    <form method="post" enctype="multipart/form-data" action="/imagen/upload/">
        <label for="archivo">Archivo de imagen:</label>
        <input type="file" name="file" id="archivo" required><br><br>
        <label for="paciente_id">ID del Paciente:</label>
        <input type="number" name="paciente_id" id="paciente_id" required><br><br>
        <button type="submit">Cargar Imagen</button>
    </form>
    </body></html>
    '''

@app.post("/imagen/upload/")
async def upload_image(file: UploadFile = File(...), paciente_id: str = Form(...)):
    # Guarda el archivo en disco y registra en la base de datos
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
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
    return {"filename": file.filename, "paciente_id": paciente_id, "msg": "Imagen cargada y registrada correctamente"}

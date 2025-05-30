from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import nibabel as nib
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from nilearn import plotting, image
import plotly.graph_objects as go
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

app = FastAPI()
UPLOAD_DIR = "media/imagenes"
PROCESSED_DIR = os.path.join(UPLOAD_DIR, "procesadas")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL config (same as Django)
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
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    vistas = None
    if file.filename.endswith('.nii') or file.filename.endswith('.nii.gz'):
        vistas = procesar_imagen(file_path)
    db = SessionLocal()
    try:
        imagen_db = ImagenMedica(
            nombre=file.filename,
            archivo=os.path.relpath(file_path, start=UPLOAD_DIR),
            fecha_carga=datetime.utcnow(),
            paciente_id=int(paciente_id),
            vista_axial=vistas["axial"] if vistas else None,
            vista_sagital=vistas["sagittal"] if vistas else None,
            vista_coronal=vistas["coronal"] if vistas else None
        )
        db.add(imagen_db)
        db.commit()
        db.refresh(imagen_db)
    finally:
        db.close()
    return {"filename": file.filename, "paciente_id": paciente_id, "vistas": vistas}

@app.get("/imagen/view/{filename}")
def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file_path)

@app.get("/imagen/descargar/{filename}")
def descargar_imagen(filename: str):
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(file_path, media_type="image/png", filename=filename)

@app.post("/imagen/reducir/")
def reducir_resolucion(filename: str = Form(...), target_shape: str = Form("64,64,64")):
    nii_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(nii_path):
        return JSONResponse(status_code=404, content={"error": "NIfTI file not found"})
    target_shape_tuple = tuple(map(int, target_shape.split(",")))
    img = nib.load(nii_path)
    data = img.get_fdata()
    factors = [int(np.ceil(data.shape[i] / target_shape_tuple[i])) for i in range(3)]
    reduced = data[::factors[0], ::factors[1], ::factors[2]]
    reduced_img = nib.Nifti1Image(reduced, img.affine)
    reduced_path = os.path.splitext(nii_path)[0] + '_reducida.nii'
    nib.save(reduced_img, reduced_path)
    return {"reduced_file": os.path.basename(reduced_path)}

@app.get("/imagen/vista_previa/{filename}")
def generar_vista_previa(filename: str, slice_index: int = Query(100)):
    nii_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(nii_path):
        return JSONResponse(status_code=404, content={"error": "NIfTI file not found"})
    img = nib.load(nii_path)
    data = img.get_fdata()
    slice_data = data[:, :, slice_index] if data.ndim == 3 else data[:, :]
    plt.axis('off')
    plt.imshow(slice_data.T, cmap='gray', origin='lower')
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    buffer.seek(0)
    return FileResponse(buffer, media_type="image/png")

@app.get("/imagen/vista_3d/{filename}")
def generar_vista_3d(filename: str):
    nii_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(nii_path):
        return JSONResponse(status_code=404, content={"error": "NIfTI file not found"})
    img = nib.load(nii_path)
    data = img.get_fdata()
    x, y, z = np.mgrid[0:data.shape[0], 0:data.shape[1], 0:data.shape[2]]
    fig = go.Figure(data=go.Volume(
        x=x.flatten(),
        y=y.flatten(),
        z=z.flatten(),
        value=data.flatten(),
        opacity=0.1,
        surface_count=20
    ))
    output_path = os.path.splitext(nii_path)[0] + '_3d.html'
    fig.write_html(output_path)
    return FileResponse(output_path, media_type="text/html")

@app.get("/imagen/vistas_2d/{filename}")
def generar_vistas_2d(filename: str):
    nii_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(nii_path):
        return JSONResponse(status_code=404, content={"error": "NIfTI file not found"})
    img = image.load_img(nii_path)
    base_name = os.path.splitext(os.path.basename(nii_path))[0]
    axial_path = os.path.join(PROCESSED_DIR, f"{base_name}_axial.png")
    sagittal_path = os.path.join(PROCESSED_DIR, f"{base_name}_sagittal.png")
    coronal_path = os.path.join(PROCESSED_DIR, f"{base_name}_coronal.png")
    if not os.path.exists(axial_path):
        plotting.plot_img(img, display_mode='z', output_file=axial_path, title="Vista Axial")
    if not os.path.exists(sagittal_path):
        plotting.plot_img(img, display_mode='x', output_file=sagittal_path, title="Vista Sagital")
    if not os.path.exists(coronal_path):
        plotting.plot_img(img, display_mode='y', output_file=coronal_path, title="Vista Coronal")
    return {
        "axial": os.path.relpath(axial_path, start=UPLOAD_DIR),
        "sagittal": os.path.relpath(sagittal_path, start=UPLOAD_DIR),
        "coronal": os.path.relpath(coronal_path, start=UPLOAD_DIR)
    }

def procesar_imagen(nii_path):
    img = image.load_img(nii_path)
    base_name = os.path.splitext(os.path.basename(nii_path))[0]
    axial_path = os.path.join(PROCESSED_DIR, f"{base_name}_axial.png")
    sagittal_path = os.path.join(PROCESSED_DIR, f"{base_name}_sagittal.png")
    coronal_path = os.path.join(PROCESSED_DIR, f"{base_name}_coronal.png")
    plotting.plot_img(img, display_mode='z', output_file=axial_path, title="Vista Axial")
    plotting.plot_img(img, display_mode='x', output_file=sagittal_path, title="Vista Sagital")
    plotting.plot_img(img, display_mode='y', output_file=coronal_path, title="Vista Coronal")
    return {
        "axial": os.path.relpath(axial_path, start=UPLOAD_DIR),
        "sagittal": os.path.relpath(sagittal_path, start=UPLOAD_DIR),
        "coronal": os.path.relpath(coronal_path, start=UPLOAD_DIR)
    }

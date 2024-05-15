from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import qrcode
import uuid
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class QRCode(Base):
    __tablename__ = "qrcodes"
    id = Column(String, primary_key=True, index=True)
    data = Column(Text)

Base.metadata.create_all(bind=engine)

class QRCodePayload(BaseModel):
    data: dict

@app.post("/generate-qr-code")
async def generate_qr_code(payload: QRCodePayload):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    unique_id = str(uuid.uuid4())
    qr.add_data(unique_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    try:
        db = SessionLocal()
        db_qrcode = QRCode(id=unique_id, data=payload.dict())
        db.add(db_qrcode)
        db.commit()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error saving data to database")

    return JSONResponse(content={"qr_code": img.tobytes().decode('latin-1')})

@app.get("/display-data/{unique_id}")
async def display_data(unique_id: str):
    try:
        db = SessionLocal()
        db_qrcode = db.query(QRCode).filter(QRCode.id == unique_id).first()
        if db_qrcode is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return JSONResponse(content={"data": db_qrcode.data})
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error retrieving data from database")
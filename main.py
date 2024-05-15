from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import qrcode
import uuid
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
import base64

app = FastAPI()

# Allow CORS for all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class QRCode(Base):
    """Database model for storing QR codes."""
    __tablename__ = "qrcodes"
    id = Column(String, primary_key=True, index=True)
    data = Column(Text)

# Create the database tables
Base.metadata.create_all(bind=engine)

class QRCodePayload(BaseModel):
    """Pydantic model for the QR code payload."""
    data: dict

@app.post("/generate-qr-code")
async def generate_qr_code(payload: QRCodePayload):
    """
    Generate a QR code for the given payload.

    Args:
        payload (QRCodePayload): The payload containing data to be stored in the QR code.

    Returns:
        JSONResponse: A JSON response containing the base64 encoded QR code image and the unique ID.
    
    Example:
        POST /generate-qr-code
        {
            "data": {"key": "value"}
        }
    """
    unique_id = str(uuid.uuid4())
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    try:
        db = SessionLocal()
        db_qrcode = QRCode(id=unique_id, data=str(payload.data))
        db.add(db_qrcode)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error saving data to database")
    finally:
        db.close()

    return JSONResponse(content={"qr_code": img_str, "id": unique_id})

@app.get("/display-data/{unique_id}")
async def display_data(unique_id: str):
    """
    Retrieve and display data stored with the given unique ID.

    Args:
        unique_id (str): The unique ID associated with the data.

    Returns:
        JSONResponse: A JSON response containing the stored data.
    
    Example:
        GET /display-data/{unique_id}
    """
    try:
        db = SessionLocal()
        db_qrcode = db.query(QRCode).filter(QRCode.id == unique_id).first()
        if db_qrcode is None:
            raise HTTPException(status_code=404, detail="Data not found")
        return JSONResponse(content={"data": db_qrcode.data})
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error retrieving data from database")
    finally:
        db.close()

# Example usage of the FastAPI app

# 1. Start the FastAPI server:
#    uvicorn main:app --reload

# 2. Generate a QR code:
#    POST http://localhost:8000/generate-qr-code
#    Body:
#    {
#        "data": {"key": "value"}
#    }

# 3. Display data:
#    GET http://localhost:8000/display-data/{unique_id}

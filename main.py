from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models import Telemetria
from database import Base, engine, async_session
import io
import csv

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session

@app.post("/telemetria")
async def recibir_datos(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    entrada = Telemetria(
        accX=data.get("accX"),
        accY=data.get("accY"),
        accZ=data.get("accZ"),
        temp=data.get("temp"),
        alt=data.get("alt"),
        comentario=data.get("comentario", "")
    )
    db.add(entrada)
    await db.commit()
    return {"status": "ok"}

@app.get("/telemetria")
async def obtener_datos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Telemetria))
    datos = result.scalars().all()
    return [
        {
            "timestamp": d.timestamp.isoformat(),
            "accX": d.accX,
            "accY": d.accY,
            "accZ": d.accZ,
            "temp": d.temp,
            "alt": d.alt,
            "comentario": d.comentario
        } for d in datos
    ]

@app.get("/descargar_csv")
async def descargar_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Telemetria))
    datos = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "accX", "accY", "accZ", "temp", "alt", "comentario"])
    for d in datos:
        writer.writerow([d.timestamp, d.accX, d.accY, d.accZ, d.temp, d.alt, d.comentario])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=telemetria.csv"})

@app.post("/resetear")
async def resetear_base(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Telemetria))
    await db.commit()
    return JSONResponse({"status": "base de datos vaciada"})

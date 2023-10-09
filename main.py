from fastapi import FastAPI, Query
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import json
from typing import List, Optional
from dotenv import load_dotenv
import os
load_dotenv();

# Create FastAPI app
app = FastAPI()

# Database connection settings
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_BD = os.getenv("DB_BD")

# SQLAlchemy database connection
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_BD}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load IBGE municipios data from JSON file
with open("ibge_municipios.json", "r") as json_file:
    ibge_municipios_data = json.load(json_file)

# Define Pydantic models for request and response
class CropRequest(BaseModel):
    cod_variavel: int
    cod_produto_lavouras_temporarias: int
    cod_ano: int
    cod_municipio: int

class CropResponse(BaseModel):
    cod_nivel_territorial: List[int]
    nivel_territorial: List[str]
    cod_unidade_medida: List[int]
    unidade_medida: List[str]
    valor: List[float]
    cod_municipio: List[int]
    nome_municipio: List[str]
    cod_ano: List[int]
    ano: List[int]
    cod_produto_lavouras_temporarias: List[int]
    produto_lavouras_temporarias: List[str]
    cod_variavel: List[int]
    variavel: List[str]

# Define API endpoint to fetch crop data
@app.get("/crop/", response_model=CropResponse)
def get_crop_data(
    cod_variavel: int = Query(..., description="Code for the variable"),
    cod_produto_lavouras_temporarias: int = Query(..., description="Code for the crop product"),
    cod_ano: int = Query(..., description="Year code"),
    cod_municipio: int = Query(..., description="IBGE code for the municipality"),
):
    # Fetch data from the database based on query parameters
    with SessionLocal() as db:
        
        sql_query = text(f"""
            SELECT *
            FROM crop.crop_data
            WHERE
                cod_variavel = {cod_variavel}
                AND cod_produto_lavouras_temporarias = {cod_produto_lavouras_temporarias}
                AND cod_ano = {cod_ano}
                AND cod_municipio = {cod_municipio}
            """)

        query = db.execute(sql_query)

        results = query.fetchall()

        if not results:
            return {"message": "No data found for the provided parameters."}

        # Convert results to the response model format
        response_data = {
            "cod_nivel_territorial": [row.cod_nivel_territorial for row in results],
            "nivel_territorial": [row.nivel_territorial for row in results],
            "cod_unidade_medida": [row.cod_unidade_medida for row in results],
            "unidade_medida": [row.unidade_medida for row in results],
            "valor": [row.valor for row in results],
            "cod_municipio": [row.cod_municipio for row in results],
            "nome_municipio": [[i for i in ibge_municipios_data if i['ibge_code'] == cod_municipio][0]['municipio']],
            "cod_ano": [row.cod_ano for row in results],
            "ano": [row.ano for row in results],
            "cod_produto_lavouras_temporarias": [row.cod_produto_lavouras_temporarias for row in results],
            "produto_lavouras_temporarias": [row.produto_lavouras_temporarias for row in results],
            "cod_variavel": [row.cod_variavel for row in results],
            "variavel": [row.variavel for row in results],
        }

        return response_data

# # Define API endpoint to fetch IBGE municipios data by code
# @app.get("/ibge_municipios/{ibge_code}")
# def get_ibge_municipio(ibge_code: int):
#     for municipio in ibge_municipios_data:
#         if municipio["ibge_code"] == ibge_code:
#             return municipio

#     return {"message": "Municipio not found for the provided code."}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

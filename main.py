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

app = FastAPI()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_BD = os.getenv("DB_BD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_BD}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

with open("ibge_municipios.json", "r") as json_file:
    ibge_municipios_data = json.load(json_file)

class CropRequest(BaseModel):
    cod_variavel: int
    cod_produto_lavouras_temporarias: int
    cod_ano: int
    cod_municipio: int

class CropResponse(BaseModel):
    cod_nivel_territorial: int
    nivel_territorial: str
    cod_unidade_medida: int
    unidade_medida: str
    valor: float
    cod_municipio: int
    nome_municipio: str
    cod_ano: int
    ano: int
    cod_produto_lavouras_temporarias: int
    produto_lavouras_temporarias: str
    cod_variavel: int
    variavel: str

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
            "cod_nivel_territorial": [row.cod_nivel_territorial for row in results][0],
            "nivel_territorial": [row.nivel_territorial for row in results][0],
            "cod_unidade_medida": [row.cod_unidade_medida for row in results][0],
            "unidade_medida": [row.unidade_medida for row in results][0],
            "valor": [row.valor for row in results][0],
            "cod_municipio": [row.cod_municipio for row in results][0],
            "nome_municipio": [i for i in ibge_municipios_data if i['ibge_code'] == cod_municipio][0]['municipio'],
            "cod_ano": [row.cod_ano for row in results][0],
            "ano": [row.ano for row in results][0],
            "cod_produto_lavouras_temporarias": [row.cod_produto_lavouras_temporarias for row in results][0],
            "produto_lavouras_temporarias": [row.produto_lavouras_temporarias for row in results][0],
            "cod_variavel": [row.cod_variavel for row in results][0],
            "variavel": [row.variavel for row in results][0],
        }

        return response_data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

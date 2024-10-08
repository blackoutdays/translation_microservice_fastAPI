from fastapi import FastAPI, HTTPException, Body
from app.services import dynamic_translate_recursive, dynamic_translate_english_recursive
from typing import Any
import logging
from app.models import ProductModel
from app.database import Database
app = FastAPI(
    title="Translation API",
    description="API для перевода данных и отправки их в другой микросервис.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

logger = logging.getLogger(__name__)

db = Database()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.post("/translate/")
async def mass_translate(data: Any = Body(...)):
    try:
        translated_data = await dynamic_translate_recursive(data)
        return {
            'status': 'success',
            'translated_data': translated_data
        }
    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/translate/english/dynamic/")
async def mass_translate_english(data: Any = Body(...)):
    try:
        translated_data = await dynamic_translate_english_recursive(data)
        return {
            'status': 'success',
            'translated_data': translated_data
        }
    except Exception as e:
        logger.error(f"Ошибка в процессе перевода: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.post("/save_product/")
async def save_product(data: ProductModel):
    try:
        product_query = """
        INSERT INTO products (description)
        VALUES ($1)
        RETURNING product_id
        """
        product_id = await db.fetchval(product_query, data.description)

        if not product_id:
            logger.error("Ошибка вставки продукта")
            raise HTTPException(status_code=500, detail="Ошибка вставки продукта")

        logger.info(f"Product ID: {product_id}")

        for lang_code, name in data.names.items():
            name_query = """
            INSERT INTO product_names (product_id, lang_code, name)
            VALUES ($1, $2, $3)
            """
            await db.execute(name_query, product_id, lang_code, name)

        return {"status": "success", "message": f"Продукт с ID {product_id} успешно сохранен."}

    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка при сохранении продукта")
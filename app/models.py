from typing import Any
from pydantic import BaseModel
from typing import Dict

class TranslationRequest(BaseModel):
    data: Any

class EnglishTranslationRequest(BaseModel):
    data: Any

class ProductModel(BaseModel):
    productId: int
    names: Dict[str, str]
    description: str

from pydantic import BaseModel
from typing import List, Optional, Any

class SQLRequest(BaseModel):
    sql: str

class SQLResponse(BaseModel):
    result: List[dict]
    rows_affected: Optional[int] = None

class RAGRequest(BaseModel):
    query: str
    k: Optional[int] = 4

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]

### Adding elements to data
class CustomerCreate(BaseModel):
    name: str
    email: str
    country: str

class ProductCreate(BaseModel):
    name: str
    price: float

class OrderCreate(BaseModel):
    customer_id: int
    order_date: str  

class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
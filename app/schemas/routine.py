from pydantic import BaseModel

class ConflictCheckRequest(BaseModel):
    product_id_a: int
    product_id_b: int
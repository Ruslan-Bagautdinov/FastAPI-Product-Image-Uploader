from pydantic import BaseModel


class ProductImage(BaseModel):
    product_id: str
    image_link: str

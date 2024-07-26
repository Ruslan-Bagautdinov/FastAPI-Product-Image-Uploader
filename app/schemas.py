from pydantic import BaseModel


class ProductImage(BaseModel):
    """
    Schema for product image data.

    Attributes:
        product_id (str): ID of the product.
        image_link (str): Link to the product image.
    """
    product_id: str
    image_link: str

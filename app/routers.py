import asyncio

from loguru import logger

from app import pictures_uploading
from app import schemas
from app.security import auth
from app.setup import fastapi_app


@fastapi_app.post('/product-images', status_code=204, dependencies=[auth])
async def start_images_uploading(data: list[schemas.ProductImage]):
    logger.info('Start image uploading')

    products_id_to_images = {rec.product_id: rec.image_link for rec in data}
    _ = asyncio.create_task(pictures_uploading.start(products_id_to_images))

    logger.info('Return 204')

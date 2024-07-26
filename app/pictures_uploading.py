import asyncio
import sys

from loguru import logger

from app import utils

logger.remove(0)

logger.add("app.log", rotation="500 MB", compression="zip", level="DEBUG")
logger.add(sys.stdout, level="INFO")


async def start(products_id_to_images: dict[str, str]):
    logger.info('Script started')
    logger.info(f'Got {len(products_id_to_images)} rows')

    for product_id, image_link in products_id_to_images.items():
        await asyncio.sleep(0)

        logger.info(f'Start process image "{image_link}" for product({product_id})')

        img = None
        if utils.image_on_moysklad(image_link):
            download_href = await utils.get_download_href(image_link)
            img = await utils.download_image_from_moysklad(download_href)

        if img:
            cf_image_link = await utils.check_and_upload_to_cloudflare(img, f"{product_id}.jpg", product_id)
            if cf_image_link:
                await utils.update_image_link(product_id, cf_image_link)  # Ensure this is the new Cloudflare link

    logger.info('Script finished')

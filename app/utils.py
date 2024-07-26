import asyncio
import io
import re

import requests
from PIL import Image
from PIL.ImageFile import ImageFile
from firebase_admin import db
from loguru import logger
from requests import Response

from app.config import CLOUDFLARE_UPLOAD_IMAGE_URL, cloudflare_headers, moysklad_headers, CLOUDFLARE_ACCOUNT_ID


def image_on_cloudflare(image_link: str) -> bool:
    url_pattern = r'imagedelivery\.net\/'
    match = re.search(url_pattern, image_link)
    return match is not None


async def upload_to_cloudflare(img=None, filename: str = None) -> str:
    if img is None or filename is None:
        logger.warning('No image or filename provided for upload to Cloudflare')
        return None

    logger.info(f'Try upload image to cloudflare as file with name {filename}')

    img_bytes = img.getvalue()
    files = {
        'file': (filename, img_bytes, 'image/jpeg'),
        'metadata': (None, '{"key": "value"}'),
        'requireSignedURLs': (None, 'false')
    }

    response = await _post_request(CLOUDFLARE_UPLOAD_IMAGE_URL, files=files, headers=cloudflare_headers)
    data = response.json()

    if not response.ok:
        logger.warning(f'Unexpected response from cloudflare, got "{data}" with status {response.status_code}')
        response.raise_for_status()

    cf_img_link = data['result']['variants'][0]
    logger.info(f'Image as file uploaded to cloudflare, now accepted by "{cf_img_link}"')
    return cf_img_link


async def check_and_upload_to_cloudflare(img, filename, product_id):
    # Fetch the existing image link from Firebase
    products_collection = db.reference('Products')
    product_ref = products_collection.child(product_id)
    product_data = product_ref.get()

    if product_data and 'img' in product_data:
        cf_image_link = product_data['img']
        logger.info(f'Fetched img from Firebase for product({product_id}): {cf_image_link}')

        if cf_image_link.startswith("https://api.moysklad.ru/"):
            new_cf_image_link = await upload_to_cloudflare(img, filename)
            if new_cf_image_link:
                await update_image_link(product_id, new_cf_image_link)
            return new_cf_image_link
        elif cf_image_link.startswith("https://imagedelivery.net"):
            image_id = cf_image_link.split('/')[-2]  # Extract the IMAGE_ID from the URL

            existing_image_bytes = await download_image_from_cloudflare_by_id(image_id)

            if existing_image_bytes:
                existing_image = Image.open(io.BytesIO(existing_image_bytes))
                new_image = Image.open(img)

                if images_are_equal(existing_image, new_image):
                    logger.info(f'Image "{filename}" is the same as the one on Cloudflare')
                    return cf_image_link
                else:
                    logger.info(f'Image "{filename}" is different from the one on Cloudflare')
                    await delete_image_from_cloudflare_by_id(image_id)
            else:
                logger.info(f'Failed to download existing image from Cloudflare for comparison')
        else:
            logger.info(f'Unknown image link format for "{filename}"')
    else:
        logger.info(f'No existing image found on Cloudflare for "{filename}"')

    new_cf_image_link = await upload_to_cloudflare(img, filename)
    if new_cf_image_link:
        await update_image_link(product_id, new_cf_image_link)
    return new_cf_image_link


def images_are_equal(img1, img2):
    if img1.size != img2.size or img1.mode != img2.mode:
        return False

    img1_bytes = image_to_bytes(img1)
    img2_bytes = image_to_bytes(img2)

    return img1_bytes.getvalue() == img2_bytes.getvalue()


async def get_image_link_from_cloudflare(filename):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1"
    response = await _get_request(url, headers=cloudflare_headers)
    if response.status_code == 200:
        data = response.json()
        logger.debug(f"Cloudflare response data: {data}")
        images = data.get('result', [])
        for image in images:
            # Ensure image is a dictionary before calling .get()
            if isinstance(image, dict) and image.get('filename') == filename:
                return image.get('variants')[0]  # Assuming the first variant is the one we want
    else:
        logger.error(f"Failed to fetch images from Cloudflare: {response.status_code}")
    return None


async def download_image_from_cloudflare_by_id(image_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1/{image_id}/blob"
    response = await _get_request(url, headers=cloudflare_headers, stream=True)

    if response.status_code == 200:
        img_bytes = response.content  # Directly get the raw bytes from the response
        logger.info(f'Got image from Cloudflare with ID "{image_id}"')
        return img_bytes
    else:
        logger.error(
            f'Failed to download image from Cloudflare with ID "{image_id}". Status code: {response.status_code}')
        return None


async def delete_image_from_cloudflare_by_id(image_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1/{image_id}"
    response = await _delete_request(url, headers=cloudflare_headers)

    if response.status_code == 200:
        logger.info(f"Successfully deleted image with ID {image_id} from Cloudflare")
    else:
        logger.error(f"Failed to delete image with ID {image_id} from Cloudflare: {response.status_code}")


async def update_image_link(product_id: str, image_link: str):
    logger.info(f'Try update img for product({product_id})')
    products_collection = db.reference('Products')
    product_ref = products_collection.child(product_id)
    product_ref.update({'img': image_link})
    logger.info(f'Success set img={image_link} for product({product_id})')


def get_images() -> dict[str, str]:
    logger.info('Try get images from firebase')
    products_collection = db.reference('Products')
    products: dict = products_collection.get()
    images_url = {pid: products[pid]['img'] for pid in products}
    logger.info(f'Got {len(images_url)} images from firebase')
    return images_url


def image_on_moysklad(image_link: str) -> bool:
    url_pattern = r'moysklad\.ru\/'
    match = re.search(url_pattern, image_link)
    return match is not None


async def get_download_href(image_link: str):
    logger.info(f'Try get download href from "{image_link}"')
    response = await _get_request(image_link, headers=moysklad_headers)
    data = response.json()
    download_href = data['rows'][0]['meta']['downloadHref']
    logger.info(f'Got download href "{download_href}" by "{image_link}"')
    return download_href


async def download_image_from_moysklad(image_link: str):
    logger.info(f'Try download image from "{image_link}"')
    response = await _get_request(image_link, headers=moysklad_headers, stream=True)

    if response.status_code == 200:
        img = Image.open(io.BytesIO(response.content))
        img_bytes = image_to_bytes(img)
        logger.info(f'Got image from "{image_link}"')
        return img_bytes
    else:
        logger.error(f'Failed to download image from "{image_link}". Status code: {response.status_code}')
        return None


def image_to_bytes(img: ImageFile):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    image_bytes = io.BytesIO()
    img.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    return image_bytes


async def _get_request(url, params=None, headers=None, stream=False) -> Response:
    response: Response = await asyncio.to_thread(
        requests.get,
        url=url,
        params=params or {},
        headers=headers or {},
        stream=stream,
    )
    return response


async def _post_request(url, data=None, json=None, files=None, params=None, headers=None,
                        stream=None) -> requests.Response:
    response: requests.Response = await asyncio.to_thread(
        requests.post,
        url=url,
        params=params or {},
        headers=headers or {},
        stream=stream,
        data=data,
        json=json,
        files=files,
    )
    return response


async def _delete_request(url, headers=None) -> requests.Response:
    response: requests.Response = await asyncio.to_thread(
        requests.delete,
        url=url,
        headers=headers or {},
    )
    return response
import os

from dotenv import load_dotenv, find_dotenv
from firebase_admin import credentials

load_dotenv(find_dotenv())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_TOKEN = os.getenv('API_TOKEN')

CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CLOUDFLARE_KEY = os.getenv('CLOUDFLARE_KEY')
CLOUDFLARE_UPLOAD_IMAGE_URL = f'https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/images/v1'
CLOUDFLARE_SIGNING_KEY = os.getenv('CLOUDFLARE_SIGNING_KEY')

cloudflare_headers = {'Authorization': f'Bearer {CLOUDFLARE_KEY}'}

FIREBASE_URL = os.getenv('FIREBASE_URL')
FIREBASE_CERT = os.getenv('FIREBASE_CERT')

FIREBASE_CREDENTIALS = credentials.Certificate(os.path.join(BASE_DIR, FIREBASE_CERT))

MOYSKLAD_KEY = os.getenv('MOYSKLAD_KEY')
MOYSKLAD_URL = "https://api.moysklad.ru/api/remap/1.2/"

moysklad_headers = {
    "Authorization": f"Bearer {MOYSKLAD_KEY}",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json"
}

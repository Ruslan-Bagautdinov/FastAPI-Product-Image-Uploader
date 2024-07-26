from fastapi import FastAPI
from firebase_admin import initialize_app
from loguru import logger

from app.config import FIREBASE_CREDENTIALS, FIREBASE_URL

cred = FIREBASE_CREDENTIALS
firebase_url = FIREBASE_URL

logger.info(f"Credential test: {cred}")


def initialize_firebase(cred, database_url):
    try:
        app = initialize_app(cred, {'databaseURL': database_url})
        logger.info(f"Firebase initialized with URL: {database_url}")
        return app
    except ValueError as e:
        if "The default Firebase app already exists" in str(e):
            return initialize_app(cred, {'databaseURL': database_url}, name='secondary')
        else:
            raise e


logger.info(f"Firebase URL: {firebase_url}")

fb = initialize_firebase(cred, firebase_url)

logger.info(f"Firebase initialized with URL: {firebase_url}")
fastapi_app = FastAPI()

# FastAPI Product Image Uploader

This FastAPI application allows you to upload product images from MoySklad to Cloudflare Images and update the image links in Firebase. It also supports checking if an image already exists on Cloudflare, downloading both images from MoySklad and Cloudflare, comparing them, and replacing the image on Cloudflare if they are not equal.

## Features

- **Image Uploading**: Upload images from MoySklad to Cloudflare Images.
- **Image Comparison**: Compare images from MoySklad and Cloudflare to ensure the latest image is used.
- **Firebase Update**: Update the image link in Firebase with the new Cloudflare image link.
- **Logging**: Comprehensive logging using Loguru for debugging and monitoring.

## Setup

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn
- Loguru
- Firebase Admin SDK
- Requests
- PIL (Pillow)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/fastapi-product-image-uploader.git
   cd fastapi-product-image-uploader
   ```
2. Create a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```sh
pip install -r requirements.txt
```

4. Set up your environment variables by creating a .env file in the root directory with the following content:

```dotenv
API_TOKEN=your_api_token
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_KEY=your_cloudflare_key
CLOUDFLARE_SIGNING_KEY=your_cloudflare_signing_key
FIREBASE_URL=your_firebase_url
FIREBASE_CERT=path_to_your_firebase_cert_file
MOYSKLAD_KEY=your_moysklad_key
```

5. Run the application:

```sh
uvicorn main:fastapi_app --reload
```

## Usage

### API Endpoint

#### POST /product-images: 

- Start the process of uploading product images.

#### Request Body:

```json
[
  {
    "product_id": "product_id_1",
    "image_link": "https://api.moysklad.ru/image_link_1"
  },
  {
    "product_id": "product_id_2",
    "image_link": "https://api.moysklad.ru/image_link_2"
  }
]
```

#### Response:
- Status Code: 204 No Content

Logging
The application uses Loguru for logging. Logs are written to app.log with a rotation of 500 MB and compressed using zip. Additionally, logs are printed to the console with an INFO level.

Contributing
Contributions are welcome! Please open an issue or submit a pull request.

License
This project is not licensed.

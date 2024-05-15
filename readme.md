# FastAPI QR Code Generator

This is a FastAPI application that generates QR codes from JSON payloads. The QR codes contain a unique ID that is stored in a SQLite database along with the JSON payload. When the QR code is scanned, it opens a webpage that displays the JSON data associated with the unique ID.

## Installation

1. Clone this repository:

```sh
git clone https://github.com/yourusername/yourrepository.git

cd yourrepository
docker build -t my-fastapi-app .
docker run -p 4000:80 my-fastapi-app
The application will be accessible at http://localhost:4000.
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv SQLAlchemy alembic mysql-connector-python qrcode[pil]

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the command to start uvicorn, using the PORT environment variable
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

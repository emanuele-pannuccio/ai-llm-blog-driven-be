import os, json
from datetime import timedelta
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = f"projects/{os.environ.get("GCP_PROJECT_ID", "gcp-automated-blog-test")}/secrets/{os.environ.get("GCP_MYSQL_SECRET", "mysql-connection")}/versions/latest"
response = client.access_secret_version(request={"name": name})

class Config:
    SQLALCHEMY_DATABASE_URI = json.loads(response.payload.data.decode("UTF-8"))["mysql_uri"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key') 
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = True
    CORS_HEADERS = 'Content-Type'
    ALLOW_ORIGIN = os.environ.get('ALLOW_ORIGIN', "http://localhost:8080")

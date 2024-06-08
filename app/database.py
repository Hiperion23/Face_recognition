import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")

if not uri:
    raise ValueError("No MONGODB_URI found in environment variables")

client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error: {e}")

# Definir la colección de usuarios
db = client.get_database("Facial")  # Obtener la base de datos
user_collection = db["users"]  # Colección de usuarios

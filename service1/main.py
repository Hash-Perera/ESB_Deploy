import os
import asyncio
from contextlib import asynccontextmanager
import aio_pika
import json
from fastapi import FastAPI
from dotenv import load_dotenv 
from pymongo import MongoClient
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# MongoDB Connection String
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(f"MongoDB URL: {MONGO_DB_URL}") 

if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL environment variable is not set")

client = AsyncIOMotorClient(MONGO_DB_URL)
database = client.EbTest
test_collection = database.get_collection("test")

# Function to verify connection
async def verify_connection():
    try:
        # Ping the MongoDB server
        await client.admin.command("ping")
        print("MongoDB connection successful!")
    except Exception as e:
        print("MongoDB connection failed:", str(e))

async def get_records_from_mongo():
    try:
        cursor = test_collection.find()  # Async cursor
        records = await cursor.to_list(length=None)  # Convert to list
        
        # Convert ObjectId to string for serialization
        for doc in records:
            doc["_id"] = str(doc["_id"])

        print(f"✅ Fetched {len(records)} records from MongoDB")
        return records

    except Exception as e:
        print(f"❌ Error fetching records: {e}")
        return []

# ========================================================================================

app = FastAPI()

@app.get("/")
def healthCheck():
    print('🟢 Sample server is running!')
    return {"status": "Hello! Sample server is running!"}

@app.get("/records")
async def get_records():
    print('🟢 Fetching records from MongoDB')
    records = await get_records_from_mongo()  
    return records

@app.get("/db")
async def db():
    await verify_connection()
    return {"status": "MongoDB connection successful!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

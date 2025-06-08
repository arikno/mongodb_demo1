from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional, List
import certifi
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# MongoDB connection string from environment variables
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
DB_NAME = os.getenv("MONGO_DB_NAME", "search")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "person")
SEARCH_INDEX_NAME = os.getenv("MONGO_SEARCH_INDEX_NAME", "personNamePhone")
AUTOCOMPLETE_INDEX_NAME = os.getenv("MONGO_AUTOCOMPLETE_INDEX_NAME", "personNamesAutocomplete")

# Create MongoDB client with SSL certificate verification
client = MongoClient(MONGO_CONNECTION_STRING, tlsCAFile=certifi.where())
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

@app.get("/person")
async def get_person(first_name: str):
    try:
        # Perform findOne query
        result = collection.find_one({"first_name": first_name})
        
        if result is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Convert ObjectId to string for JSON serialization
        result["_id"] = str(result["_id"])
        return result
        
    except Exception as e:
        logger.error(f"Error in get_person: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/person")
async def search_person(query: str):
    try:
        # Perform Atlas Search aggregation
        pipeline = [
            {
                "$search": {
                    "index": SEARCH_INDEX_NAME,
                    "text": {
                        "path": ["first_name", "middle_name"],
                        "query": query
                    }
                }
            },
            {
                "$addFields": {
                    "score": { "$meta": "searchScore" }
                }
            }
        ]
        
        logger.info(f"Search query: {query}")
        
        # Execute aggregation and convert cursor to list
        results = list(collection.aggregate(pipeline))
        
        # Convert ObjectId to string for each document
        for result in results:
            result["_id"] = str(result["_id"])
            
        if not results:
            raise HTTPException(status_code=404, detail="No matching persons found")
            
        return results
        
    except Exception as e:
        logger.error(f"Error in search_person: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/autocomplete/person")
async def autocomplete_person(query: str):
    try:
        # Perform Atlas Search autocomplete aggregation
        pipeline = [
            {
                "$search": {
                    "index": AUTOCOMPLETE_INDEX_NAME,
                    "autocomplete": {
                        "path": "first_name",
                        "query": query
                    }
                }
            },
            {
                "$group": {
                    "_id": "$first_name"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "first_name": "$_id"
                }
            },
            {
                "$sort": {
                    "first_name": 1
                }
            }
        ]
        
        logger.info(f"Autocomplete query: {query}")
        
        # Execute aggregation and convert cursor to list
        results = list(collection.aggregate(pipeline))
        
        if not results:
            raise HTTPException(status_code=404, detail="No matching names found")
            
        return results
        
    except Exception as e:
        logger.error(f"Error in autocomplete_person: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    client.close() 
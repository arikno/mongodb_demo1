# FastAPI MongoDB Demo

This is a simple FastAPI application that connects to MongoDB and provides endpoints to query and search person data.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

### 1. GET /person
Exact lookup for a person by their first name.

**Query Parameters:**
- `first_name` (string, required): The exact first name to look up

**Example Request:**
```
GET http://localhost:8000/person?first_name=John
```

**Response:**
- 200: Returns the person's complete data if found
- 404: If no person is found with the given first name
- 500: If there's a server error

### 2. GET /search/person
Full-text search across first_name and middle_name fields with relevance scoring.

**Query Parameters:**
- `query` (string, required): The search term

**Example Request:**
```
GET http://localhost:8000/search/person?query=John
```

**Response:**
- 200: Returns an array of matching persons with search scores
- 404: If no matching persons are found
- 500: If there's a server error

### 3. GET /autocomplete/person
Autocomplete endpoint for first names, optimized for prefix matching.

**Query Parameters:**
- `query` (string, required): The prefix to search for

**Example Request:**
```
GET http://localhost:8000/autocomplete/person?query=jo
```

**Response:**
- 200: Returns an array of unique first names that match the prefix, sorted alphabetically
- 404: If no matching names are found
- 500: If there's a server error

## Interactive Documentation
You can explore and test all endpoints using the Swagger UI at:
```
http://localhost:8000/docs
``` 
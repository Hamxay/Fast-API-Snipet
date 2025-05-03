# Backedn Setup Guide

## Prerequisites
Before setting up the project, ensure you have the following installed:
- Python (>=3.13)
- [uv](https://github.com/astral-sh/uv) (Fast alternative to pip)
- Git

## Clone the Repository
```bash
git clone  
cd backend
```

## Create and Activate Virtual Environment
```bash
uv venv
.\.venv\Scripts\activate
uv sync
```

## Setup Environment Variables
Create a `.env` file in the root of your project and add the following variables:
```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name
OPENAI_API_KEY=your_openai_api_key
```


## Start the FastAPI Server
Run the FastAPI application:
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Access the API
Once the server is running, you can access the API at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

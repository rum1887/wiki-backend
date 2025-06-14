import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.auth import router as auth_router 
from .routers.wiki import router as wiki_router
from fastapi import Request
import time
from fastapi import Depends
from sqlalchemy.orm import Session
import json
# from models import WikiArticle 
# from database import get_db

app = FastAPI(debug=True)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Incoming request: {request.method} {request.url} - Processed in {process_time:.4f}s")
    return response

app.include_router(auth_router, prefix="/auth")
app.include_router(wiki_router)

connections = [] 


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from routes.chat_route import router
from migrations.create_tables import create_tables
from utils.exceptions.custom_exceptions import BrewBaseException
import uvicorn



# Lifespan — runs create_tables 


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting CAfe Shop API...")
    create_tables()
    print("Tables created and seed data loaded.")
    yield
    print("Shutting down Cafe shop API...")




# creating instancess for the fastapi classs
app = FastAPI(
    title       = "Bean & Brew Chatbot",
    description = "coffee shop assistant — Brew Buddy",
    version     = "1.0.0",
    lifespan    = lifespan
)



# CORS Middleware


app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)



# Exception Handler

@app.exception_handler(BrewBaseException)
async def brew_exception_handler(request, exc: BrewBaseException):
    return JSONResponse(
        status_code = exc.status_code,
        content     = exc.to_dict()
    )



# Router
app.include_router(router)



# Run main server

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port = 8000,reload = True)


from fastapi import FastAPI
import uvicorn
from models import Base
from urls import router as api_router
from middlewares import setup_cors
from consumers import websocket_endpoint
from database import init_db, engine


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


setup_cors(app)

app.websocket("/ws/{client_id}")(websocket_endpoint)

app.include_router(api_router)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)

from fastapi import FastAPI
from api.routes import farmer, chat, market, image_detection, weather, crops
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmer.router)
app.include_router(chat.router)
app.include_router(market.router)
app.include_router(image_detection.router)
app.include_router(weather.router)
app.include_router(crops.router)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
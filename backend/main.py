from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pantry, ocr, recipes, lookup

app = FastAPI(title="Food Expiry Tracker API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pantry.router)
app.include_router(ocr.router)
app.include_router(recipes.router)
app.include_router(lookup.router)


@app.get("/")
def root():
    return {"status": "running", "message": "Food Expiry Tracker API"}